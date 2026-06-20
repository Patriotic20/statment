from app.core.base import Base
from sqlalchemy import Integer, String, ForeignKey, Enum as SA_Enum
from sqlalchemy.orm import Mapped, mapped_column
from enum import Enum  
from app.models.mixins.id_int_pk import IdIntPk
from app.models.mixins.time_stamp_mixin import TimeStampMixin


class Floor(Enum):
    FIRST = 1
    SECOND = 2
    THIRD = 3
    FOURTH = 4


class Room(Base, IdIntPk, TimeStampMixin):
    __tablename__ = "rooms"
    
    name: Mapped[str] = mapped_column(String, nullable=False)
    floor: Mapped[int] = mapped_column(SA_Enum(Floor), nullable=False)
    faculty_id: Mapped[int] = mapped_column(Integer, ForeignKey("faculties.id"), nullable=False)

    def __repr__(self):
        return f"Room(id={self.id}, name='{self.name}', faculty_id={self.faculty_id})"