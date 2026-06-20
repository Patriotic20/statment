from app.core.base import Base
from sqlalchemy import BigInteger, Integer, ForeignKey, Enum as SA_Enum
from sqlalchemy.orm import Mapped, mapped_column
from enum import Enum
from app.models.mixins.id_int_pk import IdIntPk
from app.models.mixins.time_stamp_mixin import TimeStampMixin


class IssueType(str, Enum):
    COMPUTER = "computer"
    NETWORK = "network"
    PRINTER = "printer"


class IssueStatus(str, Enum):
    NEW = "new"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"


class Issue(Base, IdIntPk, TimeStampMixin):
    __tablename__ = "issues"

    issue_type: Mapped[IssueType] = mapped_column(SA_Enum(IssueType), nullable=False)
    status: Mapped[IssueStatus] = mapped_column(
        SA_Enum(IssueStatus), nullable=False, default=IssueStatus.NEW
    )
    employee_id: Mapped[int] = mapped_column(Integer, ForeignKey("employees.id"), nullable=False)
    telegram_id: Mapped[int] = mapped_column(BigInteger, nullable=False)

    def __repr__(self):
        return f"Issue(id={self.id}, issue_type={self.issue_type}, status={self.status}, employee_id={self.employee_id})"
