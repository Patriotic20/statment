from __future__ import annotations
from typing import Optional
from pydantic import BaseModel

from app.schemes.base import ReadBase


class FacultyBase(BaseModel):
    name: str


class FacultyCreate(FacultyBase):
    pass


class FacultyUpdate(BaseModel):
    name: Optional[str] = None


class FacultyRead(FacultyBase, ReadBase):
    pass
