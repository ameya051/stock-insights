"""update daily_recommendations schema to flat columns

Revision ID: 9c3f7b2e8d21
Revises: 7bb5f1c2a6a0
Create Date: 2025-09-17

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9c3f7b2e8d21'
down_revision = '7bb5f1c2a6a0'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add new columns as nullable for data backfill
    op.add_column('daily_recommendations', sa.Column('recommendation', sa.String(), nullable=True))
    op.add_column('daily_recommendations', sa.Column('rationale', sa.String(), nullable=True))
    op.add_column('daily_recommendations', sa.Column('change_percent', sa.Numeric(14, 12), nullable=True))
    op.add_column('daily_recommendations', sa.Column('window_days', sa.BigInteger(), nullable=True))

    # Backfill from JSONB content if it exists
    try:
        op.execute(
            """
            UPDATE daily_recommendations
            SET
              recommendation = (content->>'recommendation'),
              rationale = (content->>'rationale'),
              change_percent = NULLIF(content->>'change_percent','')::numeric,
              window_days = NULLIF(content->>'window_days','')::bigint
            WHERE content IS NOT NULL;
            """
        )
    except Exception:
        # If content column doesn't exist (fresh env), ignore backfill
        pass

    # Set columns to NOT NULL
    op.alter_column('daily_recommendations', 'recommendation', nullable=False)
    op.alter_column('daily_recommendations', 'rationale', nullable=False)
    op.alter_column('daily_recommendations', 'change_percent', nullable=False)
    op.alter_column('daily_recommendations', 'window_days', nullable=False)

    # Drop content column if present
    with op.batch_alter_table('daily_recommendations') as batch_op:
        try:
            batch_op.drop_column('content')
        except Exception:
            pass


def downgrade() -> None:
    # Add content column back
    with op.batch_alter_table('daily_recommendations') as batch_op:
        batch_op.add_column(sa.Column('content', sa.JSON(), nullable=True))

    # Copy data back into content JSON
    op.execute(
        """
        UPDATE daily_recommendations
        SET content = jsonb_build_object(
            'recommendation', recommendation,
            'rationale', rationale,
            'change_percent', change_percent,
            'window_days', window_days
        )
        """
    )

    # Drop new columns
    with op.batch_alter_table('daily_recommendations') as batch_op:
        batch_op.drop_column('window_days')
        batch_op.drop_column('change_percent')
        batch_op.drop_column('rationale')
        batch_op.drop_column('recommendation')