"""Pytest configuration and fixtures."""

from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.infrastructure.persistence.database import Base

TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+asyncpg://btv_user:btv_password@postgres:5432/conciliaai",
)

# Ensure critical security variables are available for the test environment
os.environ.setdefault(
    "SECRET_KEY",
    "chave_secreta_deve_ser_longa_e_unica_para_o_teste",
)
os.environ.setdefault("DATABASE_URL", TEST_DATABASE_URL)
os.environ.setdefault("REDIS_HOST", "redis")


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def db_engine() -> AsyncGenerator[AsyncEngine, None]:
    """Create test database engine."""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(db_engine: AsyncEngine) -> AsyncGenerator[AsyncSession, None]:
    """Provide an async database session wrapped in a transactional context."""

    async with db_engine.connect() as connection:
        transaction = await connection.begin()
        async with AsyncSession(
            bind=connection, expire_on_commit=False
        ) as session:
            await session.begin_nested()
            try:
                yield session
            finally:
                if session.in_transaction():
                    await session.rollback()
        if transaction.is_active:
            await transaction.rollback()
