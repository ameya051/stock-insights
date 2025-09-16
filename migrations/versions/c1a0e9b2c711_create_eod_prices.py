"""create eod_prices

Revision ID: c1a0e9b2c711
Revises: 5fd47aaab9ea
Create Date: 2025-09-16
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c1a0e9b2c711'
down_revision = '5fd47aaab9ea'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'eod_prices',
        sa.Column('id', sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column('symbol', sa.String(), nullable=False),
        sa.Column('trade_date', sa.Date(), nullable=False),
        sa.Column('open', sa.Numeric(20, 8), nullable=False),
        sa.Column('high', sa.Numeric(20, 8), nullable=False),
        sa.Column('low', sa.Numeric(20, 8), nullable=False),
        sa.Column('close', sa.Numeric(20, 8), nullable=False),
        sa.Column('vwap', sa.Numeric(20, 8), nullable=True),
        sa.Column('volume', sa.BigInteger(), nullable=True),
        sa.Column('change_abs', sa.Numeric(20, 8), nullable=True),
        sa.Column('change_percent', sa.Numeric(14, 12), nullable=True),
        sa.Column('ingested_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    op.create_unique_constraint(
        "uq_eod_prices_symbol_date", "eod_prices", ["symbol", "trade_date"]
    )


def downgrade() -> None:
    op.drop_table('eod_prices')
