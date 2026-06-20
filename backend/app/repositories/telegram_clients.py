from app.repositories.base import BaseRepository
from app.models.telegram_clients import TelegramClient
from app.schemes.telegram_clients import TelegramLinkRequest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional


class TelegramClientRepository(BaseRepository[TelegramClient, TelegramLinkRequest, TelegramLinkRequest]):
    def __init__(self):
        super().__init__(TelegramClient)

    async def get_by_telegram_id(
        self, session: AsyncSession, telegram_id: int
    ) -> Optional[TelegramClient]:
        stmt = select(TelegramClient).where(TelegramClient.telegram_id == telegram_id)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()


telegram_client_repo = TelegramClientRepository()
