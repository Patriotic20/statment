from app.core.base import Base
from sqlalchemy import Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from app.models.mixins.id_int_pk import IdIntPk
from app.models.mixins.time_stamp_mixin import TimeStampMixin

class Statement(Base, IdIntPk, TimeStampMixin):
    __tablename__ = "statements"
    
    description: Mapped[str] = mapped_column(String, nullable=False)
    
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    room_id: Mapped[int] = mapped_column(Integer, ForeignKey("rooms.id"), nullable=False)
    employee_id: Mapped[int] = mapped_column(Integer, ForeignKey("employees.id"), nullable=False)
    
    
    
    
    def __repr__(self):
        return f"Statement(id={self.id})"