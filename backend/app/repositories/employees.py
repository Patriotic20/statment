from app.repositories.base import BaseRepository
from app.models.employees import Employee
from app.schemes.employees import EmployeeCreate, EmployeeUpdate
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional

class EmployeeRepository(BaseRepository[Employee, EmployeeCreate, EmployeeUpdate]):
    def __init__(self):
        super().__init__(Employee)
        
    async def get_by_jshir(self, session: AsyncSession, jshir: str) -> Optional[Employee]:
        stmt = select(Employee).where(Employee.jshir == jshir)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

employee_repo = EmployeeRepository()
