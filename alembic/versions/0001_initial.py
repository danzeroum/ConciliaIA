"""initial schema

Baseline migration that provisions the full ConciliaAI schema from the
SQLAlchemy models (``src.infrastructure.persistence.models.Base``). Using the
ORM metadata as the source of truth guarantees the migration stays in lockstep
with the models the application and the seed scripts rely on.

Revision ID: 0001_initial
Revises:
Create Date: 2026-06-03

"""
from __future__ import annotations

from alembic import op

# Make the application models importable. ``alembic/env.py`` already inserts the
# ``src`` directory on ``sys.path`` before this module is imported, so the same
# import path used everywhere else in the project works here too.
from infrastructure.persistence.models import Base

# revision identifiers, used by Alembic.
revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


# Extensions required by the GIN trigram indexes declared on the models
# (e.g. ``idx_sales_nsu_trgm``). Created up-front and idempotently so the
# migration is self-contained even on a managed database where ``init.sql`` is
# never executed.
_REQUIRED_EXTENSIONS = (
    "uuid-ossp",
    "pgcrypto",
    "pg_trgm",
    "btree_gin",
)


def upgrade() -> None:
    bind = op.get_bind()

    for extension in _REQUIRED_EXTENSIONS:
        op.execute(f'CREATE EXTENSION IF NOT EXISTS "{extension}"')

    Base.metadata.create_all(bind=bind)


def downgrade() -> None:
    bind = op.get_bind()
    Base.metadata.drop_all(bind=bind)
