from fastapi import APIRouter, Depends, HTTPException, status

from app.core.deps import SessionDep, get_current_user
from app.models.issues import IssueType
from app.rabbitmq import rabbitmq_manager
from app.repositories.inventory import inventory_repo
from app.repositories.issues import issue_repo
from app.repositories.telegram_clients import telegram_client_repo
from app.schemes.issues import IssueCreate, IssueRead, IssueUpdate
from app.websocket import manager as ws_manager

router = APIRouter(prefix="/issues", tags=["issues"])

# Сообщение о том, что за сотрудником не закреплено устройство нужного типа.
_NO_DEVICE_MESSAGE = {
    IssueType.COMPUTER: "За вами не закреплён компьютер. Создать заявку по этому типу нельзя.",
    IssueType.PRINTER: "За вами не закреплён принтер. Создать заявку по этому типу нельзя.",
}


@router.post("/", response_model=IssueRead, status_code=status.HTTP_201_CREATED)
async def create_issue(payload: IssueCreate, session: SessionDep) -> IssueRead:
    client = await telegram_client_repo.get_by_telegram_id(session, payload.telegram_id)
    if client is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Сначала привяжите ЖШИР",
        )

    # Проверка владения: заявки по компьютеру/принтеру можно создать, только
    # если за сотрудником закреплено устройство этого типа. Сеть — без проверки.
    if payload.issue_type in (IssueType.COMPUTER, IssueType.PRINTER):
        has_device = await inventory_repo.employee_has_device_type(
            session, client.employee_id, payload.issue_type
        )
        if not has_device:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=_NO_DEVICE_MESSAGE[payload.issue_type],
            )

    # Защита от спама: нельзя создать вторую незакрытую заявку того же типа.
    if await issue_repo.has_open_of_type(session, client.employee_id, payload.issue_type):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="У вас уже есть незакрытая заявка этого типа. "
                   "Дождитесь её решения, прежде чем создавать новую.",
        )

    data = {
        "telegram_id": payload.telegram_id,
        "issue_type": payload.issue_type,
        "employee_id": client.employee_id,
    }
    issue = await issue_repo.create(session, data)
    await rabbitmq_manager.publish_task(issue.id)
    issue_data = IssueRead.model_validate(issue).model_dump(mode="json")
    await ws_manager.broadcast({"type": "new_issue", "issue": issue_data})
    return issue


@router.get("/", response_model=list[IssueRead], dependencies=[Depends(get_current_user)])
async def list_issues(session: SessionDep, skip: int = 0, limit: int = 100):
    return await issue_repo.get_all(session, skip=skip, limit=limit)


@router.get("/{issue_id}", response_model=IssueRead, dependencies=[Depends(get_current_user)])
async def get_issue(issue_id: int, session: SessionDep) -> IssueRead:
    issue = await issue_repo.get(session, issue_id)
    if issue is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Issue not found")
    return issue


@router.patch("/{issue_id}", response_model=IssueRead, dependencies=[Depends(get_current_user)])
async def update_issue(issue_id: int, payload: IssueUpdate, session: SessionDep) -> IssueRead:
    issue = await issue_repo.update(session, issue_id, payload)
    if issue is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Issue not found")
    issue_data = IssueRead.model_validate(issue).model_dump(mode="json")
    await ws_manager.broadcast({"type": "issue_updated", "issue": issue_data})
    return issue
