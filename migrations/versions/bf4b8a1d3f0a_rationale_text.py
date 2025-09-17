"""alter rationale to TEXT

Revision ID: bf4b8a1d3f0a
Revises: 9c3f7b2e8d21
Create Date: 2025-09-17

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bf4b8a1d3f0a'
down_revision = '9c3f7b2e8d21'
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table('daily_recommendations') as batch_op:
        batch_op.alter_column('rationale', type_=sa.Text(), existing_nullable=False)


def downgrade() -> None:
    with op.batch_alter_table('daily_recommendations') as batch_op:
        batch_op.alter_column('rationale', type_=sa.String(), existing_nullable=False)
