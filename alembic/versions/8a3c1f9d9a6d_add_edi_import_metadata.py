"""Add EDI import metadata to transactions.

Revision ID: 8a3c1f9d9a6d
Revises: None
Create Date: 2024-05-09 00:00:00.000000
"""

from alembic import op

# revision identifiers, used by Alembic.
revision = '8a3c1f9d9a6d'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add metadata column for EDI import tracking."""
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name = 'transactions' 
                AND column_name = 'metadata'
            ) THEN
                ALTER TABLE transactions 
                ADD COLUMN metadata JSONB DEFAULT '{}'::jsonb;
                
                CREATE INDEX IF NOT EXISTS idx_transactions_metadata 
                ON transactions USING gin(metadata);
            END IF;
        END $$;
        """
    )


def downgrade() -> None:
    """Revert changes."""
    # Keep metadata column as it may be used by other features
    pass
