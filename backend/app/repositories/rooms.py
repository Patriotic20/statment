from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.base import BaseRepository
from app.models.rooms import Room
from app.schemes.rooms import RoomCreate, RoomUpdate

class RoomRepository(BaseRepository[Room, RoomCreate, RoomUpdate]):
    def __init__(self):
        super().__init__(Room)

    async def get_by_faculty(
        self, session: AsyncSession, faculty_id: int, skip: int = 0, limit: int = 100
    ) -> Sequence[Room]:
        """Кабинеты одного факультета — для выбора в боте и админке."""
        stmt = (
            select(Room)
            .where(Room.faculty_id == faculty_id)
            .order_by(Room.floor, Room.name)
            .offset(skip)
            .limit(limit)
        )
        result = await session.execute(stmt)
        return result.scalars().all()

    async def search(
        self, session: AsyncSession, query: str, limit: int = 20
    ) -> Sequence[Room]:
        """Ищет кабинет по части названия."""
        stmt = (
            select(Room)
            .where(Room.name.ilike(f"%{query.strip()}%"))
            .order_by(Room.floor, Room.name)
            .limit(limit)
        )
        result = await session.execute(stmt)
        return result.scalars().all()

room_repo = RoomRepository()
