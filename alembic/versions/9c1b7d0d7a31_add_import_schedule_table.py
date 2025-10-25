"""add import schedules table

Revision ID: 9c1b7d0d7a31
Revises: 8a3c1f9d9a6d
Create Date: 2024-05-14
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "9c1b7d0d7a31"
down_revision = "8a3c1f9d9a6d"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "import_schedules",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("acquirer", sa.String(length=50), nullable=False),
        sa.Column("schedule_type", sa.String(length=20), nullable=False),
        sa.Column("time_of_day", sa.String(length=5), nullable=False),
        sa.Column("days_to_import", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("credential_hint", sa.String(length=120), nullable=True),
        sa.Column("webhook_url", sa.String(length=255), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("last_run_at", sa.DateTime(), nullable=True),
        sa.Column("next_run_at", sa.DateTime(), nullable=True),
        sa.Column("error_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
    )
    op.create_index(
        "idx_import_schedules_tenant",
        "import_schedules",
        ["tenant_id"],
    )
    op.create_index(
        "idx_import_schedules_active",
        "import_schedules",
        ["tenant_id", "is_active"],
    )


def downgrade() -> None:
    op.drop_index("idx_import_schedules_active", table_name="import_schedules")
    op.drop_index("idx_import_schedules_tenant", table_name="import_schedules")
    op.drop_table("import_schedules")
