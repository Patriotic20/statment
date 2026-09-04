from app.repositories.base import BaseRepository
from app.models.employees import Employee
from app.models.rooms import Room
from app.schemes.employees import EmployeeCreate, EmployeeUpdate
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, Sequence

class EmployeeRepository(BaseRepository[Employee, EmployeeCreate, EmployeeUpdate]):
    def __init__(self):
        super().__init__(Employee)
        
    async def get_by_jshir(self, session: AsyncSession, jshir: str) -> Optional[Employee]:
        stmt = select(Employee).where(Employee.jshir == jshir)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_room(
        self, session: AsyncSession, room_id: int, skip: int = 0, limit: int = 100
    ) -> Sequence[Employee]:
        stmt = (
            select(Employee)
            .where(Employee.room_id == room_id)
            .order_by(Employee.full_name)
            .offset(skip)
            .limit(limit)
        )
        result = await session.execute(stmt)
        return result.scalars().all()

    async def get_by_faculty(
        self, session: AsyncSession, faculty_id: int, skip: int = 0, limit: int = 100
    ) -> Sequence[Employee]:
        stmt = (
            select(Employee)
            .join(Room, Room.id == Employee.room_id)
            .where(Room.faculty_id == faculty_id)
            .order_by(Employee.full_name)
            .offset(skip)
            .limit(limit)
        )
        result = await session.execute(stmt)
        return result.scalars().all()

employee_repo = EmployeeRepository()
