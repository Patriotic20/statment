from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, field_validator

from app.models.issues import IssueType
from app.schemes.base import ReadBase
from app.schemes.employees import EmployeeRead

_MAC_SEPARATORS = str.maketrans("", "", ":-. ")


def _normalize_mac(value: str) -> str:
    """Приводит MAC к виду AA:BB:CC:DD:EE:FF.

    Принимает любую из распространённых записей: aa:bb:cc:dd:ee:ff,
    aa-bb-cc-dd-ee-ff, aabb.ccdd.eeff, aabbccddeeff.
    """
    cleaned = value.translate(_MAC_SEPARATORS).upper()
    if len(cleaned) != 12 or any(c not in "0123456789ABCDEF" for c in cleaned):
        raise ValueError("MAC-manzil 12 ta o'n oltilik raqamdan iborat bo'lishi kerak")
    return ":".join(cleaned[i:i + 2] for i in range(0, 12, 2))


class InventoryBase(BaseModel):
    name: str
    image_url: Optional[str] = None
    ip_address: Optional[str] = None
    code: Optional[str] = None
    mac_address: Optional[str] = None
    device_type: Optional[IssueType] = None
    employee_id: int

    @field_validator("mac_address")
    @classmethod
    def validate_mac(cls, v: Optional[str]) -> Optional[str]:
        return _normalize_mac(v) if v else None


class InventoryCreate(InventoryBase):
    pass


class InventoryUpdate(BaseModel):
    name: Optional[str] = None
    image_url: Optional[str] = None
    ip_address: Optional[str] = None
    code: Optional[str] = None
    mac_address: Optional[str] = None
    device_type: Optional[IssueType] = None
    employee_id: Optional[int] = None

    @field_validator("mac_address")
    @classmethod
    def validate_mac(cls, v: Optional[str]) -> Optional[str]:
        return _normalize_mac(v) if v else None


class InventoryRead(InventoryBase, ReadBase):
    employee: Optional[EmployeeRead] = None
