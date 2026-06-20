from __future__ import annotations
from datetime import datetime, timezone, timedelta
from typing import Optional
from pydantic import BaseModel, field_serializer

from app.models.issues import IssueType, IssueStatus
from app.schemes.base import ReadBase, DISPLAY_TZ


class IssueCreate(BaseModel):
    telegram_id: int
    issue_type: IssueType


class IssueUpdate(BaseModel):
    status: Optional[IssueStatus] = None


class IssueRead(ReadBase):
    issue_type: IssueType
    status: IssueStatus
    employee_id: int
    telegram_id: int


class IssueWorkerRead(BaseModel):
    """Issue detail sent to the worker bot — includes who reported it and where."""

    id: int
    issue_type: IssueType
    status: IssueStatus
    telegram_id: int
    created_at: datetime
    employee_name: str
    employee_jshir: str
    room_name: str
    floor: int
    faculty_name: str

    @field_serializer("created_at")
    def _to_display_tz(self, value: datetime) -> datetime:
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return value.astimezone(DISPLAY_TZ)
