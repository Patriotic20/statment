from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, field_validator

from app.schemes.base import ReadBase
from app.schemes.employees import EmployeeRead, _normalize_jshir


class TelegramLinkRequest(BaseModel):
    telegram_id: int
    jshir: str
    username: Optional[str] = None
    first_name: Optional[str] = None

    @field_validator("jshir")
    @classmethod
    def validate_jshir(cls, v: str) -> str:
        return _normalize_jshir(v)


class TelegramClientRead(ReadBase):
    telegram_id: int
    employee_id: int
    telegram_username: Optional[str] = None
    telegram_first_name: Optional[str] = None
    employee: Optional[EmployeeRead] = None
