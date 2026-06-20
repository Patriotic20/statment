from app.core.base import Base
from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from enum import Enum  
from app.models.mixins.id_int_pk import IdIntPk
from app.models.mixins.time_stamp_mixin import TimeStampMixin

class Employee(Base, IdIntPk, TimeStampMixin):
    __tablename__ = "employees"
    
    jshir: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String, nullable=False)
    room_id: Mapped[int] = mapped_column(Integer, ForeignKey("rooms.id"), nullable=False)

    def __repr__(self):
        return f"Employee(id={self.id}, jshir='{self.jshir}', full_name='{self.full_name}', room_id={self.room_id})"