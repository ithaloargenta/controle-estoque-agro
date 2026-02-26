"""add_default_uuid_estoque

Revision ID: 962085a78481
Revises: 7606e3e0f60a
Create Date: 2026-02-26 14:47:52.951187

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '962085a78481'
down_revision: Union[str, Sequence[str], None] = '7606e3e0f60a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        ALTER TABLE estoque
        ALTER COLUMN id SET DEFAULT gen_random_uuid();
    """)


def downgrade() -> None:
    op.execute("""
        ALTER TABLE estoque
        ALTER COLUMN id DROP DEFAULT;
    """)