from app.core.base import Base
from sqlalchemy import Integer, String, Boolean, DateTime, ForeignKey, Enum as SA_Enum
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from typing import Optional
from app.models.issues import IssueType
from app.models.mixins.id_int_pk import IdIntPk
from app.models.mixins.time_stamp_mixin import TimeStampMixin

class Inventory(Base, IdIntPk, TimeStampMixin):
    __tablename__ = "inventory"

    name: Mapped[str] = mapped_column(String, nullable=False)
    image_url: Mapped[str] = mapped_column(String, nullable=True)
    ip_address: Mapped[str] = mapped_column(String, nullable=True)
    code: Mapped[str] = mapped_column(String, nullable=True)
    # Тип устройства — переиспользуем IssueType (computer/network/printer),
    # чтобы сверять с типом заявки при проверке владения.
    device_type: Mapped[Optional[IssueType]] = mapped_column(SA_Enum(IssueType), nullable=True)


    employee_id: Mapped[int] = mapped_column(Integer, ForeignKey("employees.id"), nullable=False)
    
    
    
    def __repr__(self):
        return f"Inventory(id={self.id}, name='{self.name}', code='{self.code}', employee_id={self.employee_id})"