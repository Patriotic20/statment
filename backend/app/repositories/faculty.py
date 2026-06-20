from app.repositories.base import BaseRepository
from app.models.faculty import Faculty
from app.schemes.faculty import FacultyCreate, FacultyUpdate

class FacultyRepository(BaseRepository[Faculty, FacultyCreate, FacultyUpdate]):
    def __init__(self):
        super().__init__(Faculty)

faculty_repo = FacultyRepository()
