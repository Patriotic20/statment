from app.core.base import Base
from sqlalchemy import BigInteger, Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from typing import Optional
from app.models.mixins.id_int_pk import IdIntPk
from app.models.mixins.time_stamp_mixin import TimeStampMixin


class User(Base, IdIntPk, TimeStampMixin):

    __tablename__ = "users"

    username: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String, nullable=False)
    telegram_id: Mapped[Optional[int]] = mapped_column(BigInteger, unique=True, nullable=True, default=None)
    faculty_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("faculties.id"), nullable=True, default=None)


    def __repr__(self):
        return f"User(id={self.id}, username='{self.username}', password='{self.password}')"