from app.repositories.base import BaseRepository
from app.models.statement import Statement
from app.schemes.statement import StatementCreate, StatementUpdate

class StatementRepository(BaseRepository[Statement, StatementCreate, StatementUpdate]):
    def __init__(self):
        super().__init__(Statement)

statement_repo = StatementRepository()
