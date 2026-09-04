from contextlib import asynccontextmanager
from typing import Mapping

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError


@asynccontextmanager
async def unique_violation_as_400(messages: Mapping[str, str], default: str):
    """Превращает нарушение уникальности в 400 с понятным текстом.

    Без этого дубль ЖШИР или MAC-адреса вылетает 500-й, и бот показывает
    пользователю «Internal Server Error» вместо причины.

    `messages` — соответствие «имя constraint в БД → сообщение».
    """
    try:
        yield
    except IntegrityError as exc:
        detail = str(getattr(exc, "orig", exc))
        for constraint, message in messages.items():
            if constraint in detail:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail=message
                ) from exc
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=default
        ) from exc
