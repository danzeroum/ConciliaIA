"""add notifications and alert history tables"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "b1a3c8f5b9d1"
down_revision = "9c1b7d0d7a31"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "notifications",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column(
            "priority",
            sa.String(length=20),
            nullable=False,
            server_default=sa.text("'info'"),
        ),
        sa.Column("action_url", sa.String(length=500), nullable=True),
        sa.Column(
            "is_read",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column("read_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
    )
    op.create_index(
        "idx_notifications_tenant_created",
        "notifications",
        ["tenant_id", "created_at"],
    )
    op.create_index(
        "idx_notifications_unread",
        "notifications",
        ["tenant_id", "is_read"],
    )

    op.create_table(
        "alert_history",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("rule_id", sa.String(length=50), nullable=False),
        sa.Column(
            "triggered_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column("alert_data", postgresql.JSONB(), nullable=True),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
    )
    op.create_index(
        "idx_alert_history_tenant",
        "alert_history",
        ["tenant_id", "triggered_at"],
    )
    op.create_index(
        "idx_alert_history_rule",
        "alert_history",
        ["rule_id", "triggered_at"],
    )


def downgrade() -> None:
    op.drop_index("idx_alert_history_rule", table_name="alert_history")
    op.drop_index("idx_alert_history_tenant", table_name="alert_history")
    op.drop_table("alert_history")

    op.drop_index("idx_notifications_unread", table_name="notifications")
    op.drop_index("idx_notifications_tenant_created", table_name="notifications")
    op.drop_table("notifications")
