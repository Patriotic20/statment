from __future__ import annotations
from typing import Optional
from pydantic import BaseModel

from app.schemes.base import ReadBase


class UserBase(BaseModel):
    username: str


class UserCreate(UserBase):
    password: str
    faculty_id: Optional[int] = None


class UserUpdate(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None
    telegram_id: Optional[int] = None
    faculty_id: Optional[int] = None


class WorkerAuthRequest(BaseModel):
    telegram_id: int
    username: str
    password: str


class WorkerAuthResponse(BaseModel):
    ok: bool
    user_id: int
    faculty_id: Optional[int] = None
    # JWT воркера: с ним бот ходит в защищённые /rooms, /employees, /inventory
    # от имени этого пользователя.
    access_token: Optional[str] = None


class MiniAppAuthRequest(BaseModel):
    """Вход в Mini App по подписи Telegram, без логина и пароля."""
    init_data: str


class MiniAppLoginRequest(BaseModel):
    """Первый вход: подпись Telegram + учётные данные, чтобы связать аккаунты."""
    init_data: str
    username: str
    password: str


class MiniAppAuthResponse(BaseModel):
    access_token: str
    user_id: int
    username: str
    faculty_id: Optional[int] = None


class WorkerTelegramRead(BaseModel):
    telegram_id: int


class WorkerFacultyRequest(BaseModel):
    telegram_id: int
    faculty_id: int


class UserRead(UserBase, ReadBase):
    telegram_id: Optional[int] = None
    faculty_id: Optional[int] = None
