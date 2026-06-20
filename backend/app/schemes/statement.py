from __future__ import annotations
from typing import Optional
from pydantic import BaseModel

from app.schemes.base import ReadBase
from app.schemes.user import UserRead
from app.schemes.rooms import RoomRead
from app.schemes.employees import EmployeeRead


class StatementBase(BaseModel):
    description: str
    user_id: int
    room_id: int
    employee_id: int


class StatementCreate(StatementBase):
    pass


class StatementUpdate(BaseModel):
    description: Optional[str] = None
    user_id: Optional[int] = None
    room_id: Optional[int] = None
    employee_id: Optional[int] = None


class StatementRead(StatementBase, ReadBase):
    user: Optional[UserRead] = None
    room: Optional[RoomRead] = None
    employee: Optional[EmployeeRead] = None
