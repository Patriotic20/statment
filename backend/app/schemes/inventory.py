from __future__ import annotations
from typing import Optional
from pydantic import BaseModel

from app.models.issues import IssueType
from app.schemes.base import ReadBase
from app.schemes.employees import EmployeeRead


class InventoryBase(BaseModel):
    name: str
    image_url: Optional[str] = None
    ip_address: Optional[str] = None
    code: Optional[str] = None
    device_type: Optional[IssueType] = None
    employee_id: int


class InventoryCreate(InventoryBase):
    pass


class InventoryUpdate(BaseModel):
    name: Optional[str] = None
    image_url: Optional[str] = None
    ip_address: Optional[str] = None
    code: Optional[str] = None
    device_type: Optional[IssueType] = None
    employee_id: Optional[int] = None


class InventoryRead(InventoryBase, ReadBase):
    employee: Optional[EmployeeRead] = None
