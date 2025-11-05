"""Alembic environment configuration."""

from __future__ import annotations
import os
import sys
from logging.config import fileConfig
from pathlib import Path

from alembic import context
from sqlalchemy import engine_from_config, pool

# --- Load application Base ---
# Garantir que o Alembic encontre o diretório src/
project_root = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(project_root))

# Agora podemos importar corretamente o Base
from infrastructure.persistence.models import Base

# Alembic Config object
config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

# --- Database URL ---
# Garante que Alembic use psycopg2 mesmo que a app use asyncpg
database_url = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://btv_user:btv_password@postgres:5432/buildtovalue"
).replace("asyncpg", "psycopg2")

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    context.configure(
        url=database_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        url=database_url,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
