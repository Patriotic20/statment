from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.base import BaseRepository
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

inventory_repo = InventoryRepository()
