"""add mac_address to inventory

Revision ID: f4a6b8c0d2e3
Revises: e3f5a7b9c1d2
Create Date: 2026-09-04 12:40:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'f4a6b8c0d2e3'
down_revision: Union[str, Sequence[str], None] = 'e3f5a7b9c1d2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('inventory', sa.Column('mac_address', sa.String(), nullable=True))
    op.create_unique_constraint('inventory_mac_address_key', 'inventory', ['mac_address'])


def downgrade() -> None:
    op.drop_constraint('inventory_mac_address_key', 'inventory', type_='unique')
    op.drop_column('inventory', 'mac_address')
