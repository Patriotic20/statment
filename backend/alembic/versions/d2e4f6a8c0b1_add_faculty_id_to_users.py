"""add faculty_id to users

Revision ID: d2e4f6a8c0b1
Revises: c1d3e5f7a9b2
Create Date: 2026-06-19 19:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'd2e4f6a8c0b1'
down_revision: Union[str, Sequence[str], None] = 'c1d3e5f7a9b2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'users',
        sa.Column('faculty_id', sa.Integer(), nullable=True),
    )
    op.create_foreign_key(
        'fk_users_faculty_id',
        'users', 'faculties',
        ['faculty_id'], ['id'],
    )


def downgrade() -> None:
    op.drop_constraint('fk_users_faculty_id', 'users', type_='foreignkey')
    op.drop_column('users', 'faculty_id')
