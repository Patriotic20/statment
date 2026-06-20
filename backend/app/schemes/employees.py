from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, field_validator

from app.schemes.base import ReadBase
from app.schemes.rooms import RoomRead


def _normalize_jshir(value: str) -> str:
    """Удаляет все пробелы и проверяет, что ЖШИР — ровно 14 цифр."""
    cleaned = "".join(value.split())
    if not cleaned.isdigit() or len(cleaned) != 14:
        raise ValueError("ЖШИР должен состоять ровно из 14 цифр")
    return cleaned


class EmployeeBase(BaseModel):
    jshir: str
    full_name: str
    room_id: int


class EmployeeCreate(EmployeeBase):
    @field_validator("jshir")
    @classmethod
    def validate_jshir(cls, v: str) -> str:
        return _normalize_jshir(v)


class EmployeeUpdate(BaseModel):
    jshir: Optional[str] = None
    full_name: Optional[str] = None
    room_id: Optional[int] = None

    @field_validator("jshir")
    @classmethod
    def validate_jshir(cls, v: Optional[str]) -> Optional[str]:
        return _normalize_jshir(v) if v is not None else v


class EmployeeRead(EmployeeBase, ReadBase):
    room: Optional[RoomRead] = None
