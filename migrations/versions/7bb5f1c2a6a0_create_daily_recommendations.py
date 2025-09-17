"""create daily_recommendations table

Revision ID: 7bb5f1c2a6a0
Revises: 92e044143cbf
Create Date: 2025-09-17

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '7bb5f1c2a6a0'
down_revision = '92e044143cbf'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'daily_recommendations',
        sa.Column('id', sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column('symbol', sa.String(), nullable=False),
        sa.Column('trade_date', sa.Date(), nullable=False),
        sa.Column('model_name', sa.String(), nullable=False),
        sa.Column('content', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    op.create_unique_constraint(
        'uq_daily_rec_symbol_date_model', 'daily_recommendations', ['symbol', 'trade_date', 'model_name']
    )


def downgrade() -> None:
    op.drop_constraint('uq_daily_rec_symbol_date_model', 'daily_recommendations', type_='unique')
    op.drop_table('daily_recommendations')
