"""Async database helpers built on top of asyncpg."""

from __future__ import annotations

import os
from typing import Optional

import asyncpg
import structlog

logger = structlog.get_logger(__name__)

_pool: Optional[asyncpg.Pool] = None


async def init_database_pool() -> Optional[asyncpg.Pool]:
    """Initialize a global asyncpg connection pool if configuration is present."""

    global _pool
    if _pool is not None:
        return _pool

    dsn = os.getenv("DATABASE_URL")
    if not dsn:
        host = os.getenv("DB_HOST")
        if not host:
            logger.warning("database_pool_not_configured")
            return None
        user = os.getenv("DB_USER", "postgres")
        password = os.getenv("DB_PASSWORD", "postgres")
        database = os.getenv("DB_NAME", "postgres")
        port = int(os.getenv("DB_PORT", "5432"))
        dsn = f"postgresql://{user}:{password}@{host}:{port}/{database}"

    try:
        _pool = await asyncpg.create_pool(dsn=dsn, min_size=1, max_size=5)
        logger.info("database_pool_initialized")
    except Exception as exc:  # pragma: no cover - defensive fallback
        logger.warning("database_pool_init_failed", error=str(exc))
        _pool = None

    return _pool


async def get_pool() -> Optional[asyncpg.Pool]:
    """Return the current pool instance."""

    return _pool


async def close_database_pool() -> None:
    """Dispose of the asyncpg pool if it exists."""

    global _pool
    if _pool is None:
        return

    await _pool.close()
    _pool = None
    logger.info("database_pool_closed")


__all__ = ["init_database_pool", "close_database_pool", "get_pool"]
