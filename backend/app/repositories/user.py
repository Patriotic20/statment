from app.repositories.base import BaseRepository
from app.models.user import User
from app.schemes.user import UserCreate, UserUpdate
from app.core.security import hash_password
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Any, Dict, Optional, Union

class UserRepository(BaseRepository[User, UserCreate, UserUpdate]):
    def __init__(self):
        super().__init__(User)

    async def create(self, session: AsyncSession, obj_in: Union[UserCreate, Dict[str, Any]]) -> User:
        data = obj_in if isinstance(obj_in, dict) else obj_in.model_dump(exclude_unset=True)
        if "password" in data and data["password"] is not None:
            data["password"] = hash_password(data["password"])
        return await super().create(session, data)

    async def update(self, session: AsyncSession, id: int, obj_in: Union[UserUpdate, Dict[str, Any]]) -> Optional[User]:
        data = obj_in if isinstance(obj_in, dict) else obj_in.model_dump(exclude_unset=True)
        if "password" in data and data["password"] is not None:
            data["password"] = hash_password(data["password"])
        return await super().update(session, id, data)

    async def get_by_username(self, session: AsyncSession, username: str) -> Optional[User]:
        stmt = select(User).where(User.username == username)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_telegram_id(self, session: AsyncSession, telegram_id: int) -> Optional[User]:
        stmt = select(User).where(User.telegram_id == telegram_id)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def link_telegram_id(self, session: AsyncSession, user_id: int, telegram_id: int) -> Optional[User]:
        return await self.update(session, user_id, {"telegram_id": telegram_id})

    async def get_all_with_telegram(self, session: AsyncSession) -> list[User]:
        stmt = select(User).where(User.telegram_id.is_not(None))
        result = await session.execute(stmt)
        return list(result.scalars().all())

    async def get_workers_by_faculty(self, session: AsyncSession, faculty_id: int) -> list[User]:
        stmt = select(User).where(
            User.faculty_id == faculty_id,
            User.telegram_id.is_not(None),
        )
        result = await session.execute(stmt)
        return list(result.scalars().all())

user_repo = UserRepository()
