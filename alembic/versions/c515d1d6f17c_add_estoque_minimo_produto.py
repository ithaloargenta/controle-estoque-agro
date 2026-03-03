"""add_estoque_minimo_produto

Revision ID: c515d1d6f17c
Revises: 02406df23f45
Create Date: 2026-03-03 13:31:46.975516

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'c515d1d6f17c'
down_revision: Union[str, Sequence[str], None] = '02406df23f45'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'produto',
        sa.Column('estoque_minimo', sa.Integer(), nullable=False, server_default='2')
    )


def downgrade() -> None:
    op.drop_column('produto', 'estoque_minimo')