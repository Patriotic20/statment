from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.base import BaseRepository
from app.models.issues import Issue, IssueStatus, IssueType
from app.models.employees import Employee
from app.models.faculty import Faculty
from app.models.rooms import Room
from app.schemes.issues import IssueCreate, IssueUpdate


class IssueRepository(BaseRepository[Issue, IssueCreate, IssueUpdate]):
    def __init__(self):
        super().__init__(Issue)

    async def has_open_of_type(
        self, session: AsyncSession, employee_id: int, issue_type: IssueType
    ) -> bool:
        """Есть ли у сотрудника незакрытая (status != resolved) заявка этого типа."""
        stmt = (
            select(Issue.id)
            .where(
                Issue.employee_id == employee_id,
                Issue.issue_type == issue_type,
                Issue.status != IssueStatus.RESOLVED,
            )
            .limit(1)
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def get_detail(self, session: AsyncSession, issue_id: int) -> dict | None:
        """Issue joined with its employee, room and faculty for worker notifications."""
        stmt = (
            select(
                Issue.id,
                Issue.issue_type,
                Issue.status,
                Issue.telegram_id,
                Issue.created_at,
                Employee.full_name.label("employee_name"),
                Employee.jshir.label("employee_jshir"),
                Room.name.label("room_name"),
                Room.floor,
                Faculty.name.label("faculty_name"),
            )
            .select_from(Issue)
            .join(Employee, Employee.id == Issue.employee_id)
            .join(Room, Room.id == Employee.room_id)
            .join(Faculty, Faculty.id == Room.faculty_id)
            .where(Issue.id == issue_id)
        )
        result = await session.execute(stmt)
        row = result.mappings().one_or_none()
        if row is None:
            return None
        data = dict(row)
        data["floor"] = data["floor"].value
        return data

    async def get_faculty_id(self, session: AsyncSession, issue_id: int) -> int | None:
        stmt = (
            select(Room.faculty_id)
            .select_from(Issue)
            .join(Employee, Employee.id == Issue.employee_id)
            .join(Room, Room.id == Employee.room_id)
            .where(Issue.id == issue_id)
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none()


issue_repo = IssueRepository()
