from app.core.base import Base
from sqlalchemy import BigInteger, String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.models.mixins.id_int_pk import IdIntPk
from app.models.mixins.time_stamp_mixin import TimeStampMixin


class TelegramClient(Base, IdIntPk, TimeStampMixin):
    __tablename__ = "telegram_clients"

    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    employee_id: Mapped[int] = mapped_column(Integer, ForeignKey("employees.id"), nullable=False)
    telegram_username: Mapped[str | None] = mapped_column(String, nullable=True)
    telegram_first_name: Mapped[str | None] = mapped_column(String, nullable=True)

    def __repr__(self):
        return f"TelegramClient(id={self.id}, telegram_id={self.telegram_id}, employee_id={self.employee_id})"
