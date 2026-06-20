from app.core.base import Base
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from app.models.mixins.id_int_pk import IdIntPk
from app.models.mixins.time_stamp_mixin import TimeStampMixin


class Faculty(Base, IdIntPk, TimeStampMixin):
    __tablename__ = "faculties"
    
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)

    def __repr__(self):
        return f"Faculty(id={self.id}, name='{self.name}')"