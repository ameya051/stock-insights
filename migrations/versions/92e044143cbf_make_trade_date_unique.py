"""make trade_date unique

Revision ID: 92e044143cbf
Revises: e2d61924fd73
Create Date: 2025-09-17 00:48:41.606507

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '92e044143cbf'
down_revision = 'e2d61924fd73'
branch_labels = None
depends_on = None

def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
