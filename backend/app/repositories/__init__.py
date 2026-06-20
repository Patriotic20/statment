from .base import BaseRepository
from .user import user_repo, UserRepository
from .faculty import faculty_repo, FacultyRepository
from .rooms import room_repo, RoomRepository
from .employees import employee_repo, EmployeeRepository
from .inventory import inventory_repo, InventoryRepository
from .statement import statement_repo, StatementRepository

__all__ = [
    "BaseRepository",
    "user_repo", "UserRepository",
    "faculty_repo", "FacultyRepository",
    "room_repo", "RoomRepository",
    "employee_repo", "EmployeeRepository",
    "inventory_repo", "InventoryRepository",
    "statement_repo", "StatementRepository",
]
