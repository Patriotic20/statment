from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.core.deps import SessionDep, get_current_user
from app.repositories.faculty import faculty_repo
from app.repositories.user import user_repo
from app.schemes.user import UserCreate, UserRead

router = APIRouter(
    prefix="/users",
    tags=["users"],
    dependencies=[Depends(get_current_user)],
)


class FacultyBody(BaseModel):
    faculty_id: Optional[int] = None


@router.get("/", response_model=list[UserRead])
async def list_users(session: SessionDep):
    return await user_repo.get_all(session)


@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(payload: UserCreate, session: SessionDep) -> UserRead:
    existing = await user_repo.get_by_username(session, payload.username)
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bu login allaqachon band",
        )
    if payload.faculty_id is not None and await faculty_repo.get(session, payload.faculty_id) is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Fakultet {payload.faculty_id} mavjud emas",
        )
    # Пароль хешируется в user_repo.create.
    return await user_repo.create(session, payload)


@router.patch("/{user_id}/faculty", response_model=UserRead)
async def update_user_faculty(
    user_id: int,
    body: FacultyBody,
    session: SessionDep,
) -> UserRead:
    user = await user_repo.update(session, user_id, {"faculty_id": body.faculty_id})
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user
