"""add device_type to inventory

Revision ID: e3f5a7b9c1d2
Revises: d2e4f6a8c0b1
Create Date: 2026-06-20 04:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'e3f5a7b9c1d2'
down_revision: Union[str, Sequence[str], None] = 'd2e4f6a8c0b1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Тип issuetype уже существует в БД (используется таблицей issues),
    # поэтому create_type=False — иначе миграция упадёт на CREATE TYPE.
    op.add_column(
        'inventory',
        sa.Column(
            'device_type',
            sa.Enum('COMPUTER', 'NETWORK', 'PRINTER', name='issuetype', create_type=False),
            nullable=True,
        ),
    )


def downgrade() -> None:
    op.drop_column('inventory', 'device_type')
