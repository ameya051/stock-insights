"""make trade_date unique

Revision ID: e2d61924fd73
Revises: eb66f8b711d9
Create Date: 2025-09-17 00:46:48.766453

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'e2d61924fd73'
down_revision = 'eb66f8b711d9'
branch_labels = None
depends_on = None

def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
