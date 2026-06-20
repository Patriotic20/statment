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


class WorkerTelegramRead(BaseModel):
    telegram_id: int


class WorkerFacultyRequest(BaseModel):
    telegram_id: int
    faculty_id: int


class UserRead(UserBase, ReadBase):
    telegram_id: Optional[int] = None
    faculty_id: Optional[int] = None
