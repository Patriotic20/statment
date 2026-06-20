from datetime import datetime, timezone
from sqlalchemy import DateTime
from sqlalchemy.orm import Mapped, mapped_column

def get_utc_now() -> datetime:
    """Возвращает текущее время в UTC +0"""
    return datetime.now(timezone.utc)

class TimeStampMixin:
    """
    Миксин для добавления полей created_at и updated_at.
    Время всегда сохраняется в UTC +0.
    """
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=get_utc_now,
        nullable=False
    )
    
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=get_utc_now, 
        onupdate=get_utc_now,
        nullable=False
    )
