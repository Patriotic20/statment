from fastapi import APIRouter, HTTPException, status

from app.core.deps import SessionDep
from app.repositories.employees import employee_repo
from app.repositories.issues import issue_repo
from app.repositories.telegram_clients import telegram_client_repo
from app.repositories.user import user_repo
from app.services.auth import authenticate
from app.schemes.issues import IssueRead, IssueUpdate, IssueWorkerRead
from app.schemes.telegram_clients import TelegramLinkRequest, TelegramClientRead
from app.schemes.user import (
    WorkerAuthRequest, WorkerAuthResponse,
    WorkerTelegramRead, WorkerFacultyRequest,
)
from app.websocket import manager as ws_manager

router = APIRouter(prefix="/telegram", tags=["telegram"])


@router.post("/link", response_model=TelegramClientRead)
async def link_client(payload: TelegramLinkRequest, session: SessionDep) -> TelegramClientRead:
    employee = await employee_repo.get_by_jshir(session, payload.jshir)
    if employee is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ЖШИР не найден",
        )

    existing = await telegram_client_repo.get_by_telegram_id(session, payload.telegram_id)
    data = {
        "telegram_id": payload.telegram_id,
        "employee_id": employee.id,
        "telegram_username": payload.username,
        "telegram_first_name": payload.first_name,
    }
    if existing is None:
        return await telegram_client_repo.create(session, data)
    return await telegram_client_repo.update(session, existing.id, data)


@router.get("/clients/{telegram_id}", response_model=TelegramClientRead)
async def get_client(telegram_id: int, session: SessionDep) -> TelegramClientRead:
    client = await telegram_client_repo.get_by_telegram_id(session, telegram_id)
    if client is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not linked")
    return client


@router.post("/worker/auth", response_model=WorkerAuthResponse)
async def worker_auth(payload: WorkerAuthRequest, session: SessionDep) -> WorkerAuthResponse:
    user = await authenticate(session, payload.username, payload.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный логин или пароль",
        )
    await user_repo.link_telegram_id(session, user.id, payload.telegram_id)
    # Факультет уже назначен админом в users.faculty_id — отдаём его, чтобы бот
    # не спрашивал факультет повторно.
    return WorkerAuthResponse(ok=True, user_id=user.id, faculty_id=user.faculty_id)


@router.post("/worker/faculty")
async def set_worker_faculty(payload: WorkerFacultyRequest, session: SessionDep):
    user = await user_repo.get_by_telegram_id(session, payload.telegram_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Worker not registered")
    await user_repo.update(session, user.id, {"faculty_id": payload.faculty_id})
    return {"ok": True}


@router.get("/workers", response_model=list[WorkerTelegramRead])
async def get_workers(session: SessionDep, faculty_id: int | None = None) -> list[WorkerTelegramRead]:
    if faculty_id is not None:
        users = await user_repo.get_workers_by_faculty(session, faculty_id)
    else:
        users = await user_repo.get_all_with_telegram(session)
    return [WorkerTelegramRead(telegram_id=u.telegram_id) for u in users]


@router.get("/workers/{telegram_id}", response_model=WorkerTelegramRead)
async def get_worker(telegram_id: int, session: SessionDep) -> WorkerTelegramRead:
    user = await user_repo.get_by_telegram_id(session, telegram_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Worker not registered")
    return WorkerTelegramRead(telegram_id=user.telegram_id)


@router.get("/issue-faculty/{issue_id}")
async def get_issue_faculty(issue_id: int, session: SessionDep):
    faculty_id = await issue_repo.get_faculty_id(session, issue_id)
    if faculty_id is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Issue or faculty not found")
    return {"faculty_id": faculty_id}


@router.get("/issues/{issue_id}", response_model=IssueWorkerRead)
async def get_issue_for_worker(issue_id: int, session: SessionDep) -> IssueWorkerRead:
    detail = await issue_repo.get_detail(session, issue_id)
    if detail is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Issue not found")
    return detail


@router.patch("/issues/{issue_id}", response_model=IssueRead)
async def update_issue_for_worker(
    issue_id: int, payload: IssueUpdate, session: SessionDep
) -> IssueRead:
    issue = await issue_repo.update(session, issue_id, payload)
    if issue is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Issue not found")
    issue_data = IssueRead.model_validate(issue).model_dump(mode="json")
    await ws_manager.broadcast({"type": "issue_updated", "issue": issue_data})
    return issue
