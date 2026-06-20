from __future__ import annotations
from datetime import datetime, timezone, timedelta
from pydantic import BaseModel, ConfigDict, field_serializer

# Data is stored in UTC (+0); it is displayed to users in UTC+5 (Asia/Tashkent).
DISPLAY_TZ = timezone(timedelta(hours=5))


class ReadBase(BaseModel):
    """Shared base for every Read schema.

    Provides the common `id` + timestamp fields, ORM loading, and converts
    the UTC-stored timestamps to UTC+5 for display on serialization.
    """

    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @field_serializer("created_at", "updated_at")
    def _to_display_tz(self, value: datetime) -> datetime:
        if value.tzinfo is None:
            # Stored value is UTC; tag it before converting.
            value = value.replace(tzinfo=timezone.utc)
        return value.astimezone(DISPLAY_TZ)
