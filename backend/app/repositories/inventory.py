from typing import Optional, Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.base import BaseRepository
from app.models.employees import Employee
from app.models.inventory import Inventory
from app.models.issues import IssueType
from app.schemes.inventory import InventoryCreate, InventoryUpdate

class InventoryRepository(BaseRepository[Inventory, InventoryCreate, InventoryUpdate]):
    def __init__(self):
        super().__init__(Inventory)

    async def employee_has_device_type(
        self, session: AsyncSession, employee_id: int, device_type: IssueType
    ) -> bool:
        """Закреплено ли за сотрудником устройство данного типа."""
        stmt = (
            select(Inventory.id)
            .where(
                Inventory.employee_id == employee_id,
                Inventory.device_type == device_type,
            )
            .limit(1)
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def get_by_mac(self, session: AsyncSession, mac_address: str) -> Optional[Inventory]:
        stmt = select(Inventory).where(Inventory.mac_address == mac_address)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_filtered(
        self,
        session: AsyncSession,
        employee_id: Optional[int] = None,
        room_id: Optional[int] = None,
        device_type: Optional[IssueType] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> Sequence[Inventory]:
        """Оборудование с фильтрами — по владельцу, кабинету и типу устройства."""
        stmt = select(Inventory)
        if room_id is not None:
            stmt = stmt.join(Employee, Employee.id == Inventory.employee_id).where(
                Employee.room_id == room_id
            )
        if employee_id is not None:
            stmt = stmt.where(Inventory.employee_id == employee_id)
        if device_type is not None:
            stmt = stmt.where(Inventory.device_type == device_type)
        stmt = stmt.order_by(Inventory.name).offset(skip).limit(limit)
        result = await session.execute(stmt)
        return result.scalars().all()

inventory_repo = InventoryRepository()
