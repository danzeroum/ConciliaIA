"""reconciliation jobs table

Adds the ``reconciliation_jobs`` table backing the asynchronous reconciliation
flow (POST returns 202 + job_id, status is polled).

Revision ID: 0002_reconciliation_jobs
Revises: 0001_initial
Create Date: 2026-06-04

"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "0002_reconciliation_jobs"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "reconciliation_jobs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "tenant_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("tenants.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="pending"),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=False),
        sa.Column("checkpoints", postgresql.JSONB(), nullable=True),
        sa.Column("result", postgresql.JSONB(), nullable=True),
        sa.Column("error", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("started_at", sa.DateTime(), nullable=True),
        sa.Column("finished_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_reconciliation_jobs_tenant_id", "reconciliation_jobs", ["tenant_id"])
    op.create_index("ix_reconciliation_jobs_status", "reconciliation_jobs", ["status"])
    op.create_index(
        "idx_reconciliation_jobs_tenant_status",
        "reconciliation_jobs",
        ["tenant_id", "status"],
    )
    op.create_index(
        "idx_reconciliation_jobs_tenant_created",
        "reconciliation_jobs",
        ["tenant_id", "created_at"],
    )


def downgrade() -> None:
    op.drop_index("idx_reconciliation_jobs_tenant_created", table_name="reconciliation_jobs")
    op.drop_index("idx_reconciliation_jobs_tenant_status", table_name="reconciliation_jobs")
    op.drop_index("ix_reconciliation_jobs_status", table_name="reconciliation_jobs")
    op.drop_index("ix_reconciliation_jobs_tenant_id", table_name="reconciliation_jobs")
    op.drop_table("reconciliation_jobs")
