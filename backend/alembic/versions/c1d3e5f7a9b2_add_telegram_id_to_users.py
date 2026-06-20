"""add telegram_id to users

Revision ID: c1d3e5f7a9b2
Revises: b4b29053ad3e
Create Date: 2026-06-19 18:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'c1d3e5f7a9b2'
down_revision: Union[str, Sequence[str], None] = 'b4b29053ad3e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'users',
        sa.Column('telegram_id', sa.BigInteger(), nullable=True, unique=True),
    )


def downgrade() -> None:
    op.drop_column('users', 'telegram_id')
