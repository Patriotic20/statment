from __future__ import annotations
from typing import Optional
from pydantic import BaseModel

from app.models.rooms import Floor
from app.schemes.base import ReadBase
from app.schemes.faculty import FacultyRead


class RoomBase(BaseModel):
    name: str
    floor: Floor
    faculty_id: int


class RoomCreate(RoomBase):
    pass


class RoomUpdate(BaseModel):
    name: Optional[str] = None
    floor: Optional[Floor] = None
    faculty_id: Optional[int] = None


class RoomRead(RoomBase, ReadBase):
    faculty: Optional[FacultyRead] = None
