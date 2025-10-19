"""Redis cache helpers."""

from __future__ import annotations

import os
from typing import Optional

import redis.asyncio as redis
import structlog

logger = structlog.get_logger(__name__)

_pool: Optional[redis.Redis] = None


async def init_redis_pool() -> Optional[redis.Redis]:
    """Create a Redis connection pool if configuration is available."""

    global _pool
    if _pool is not None:
        return _pool

    host = os.getenv("REDIS_HOST")
    if not host:
        logger.warning("redis_pool_not_configured")
        return None

    port = int(os.getenv("REDIS_PORT", "6379"))
    password = os.getenv("REDIS_PASSWORD")

    try:
        _pool = redis.Redis(host=host, port=port, password=password, decode_responses=True)
        await _pool.ping()
        logger.info("redis_pool_initialized")
    except Exception as exc:  # pragma: no cover - defensive fallback
        logger.warning("redis_pool_init_failed", error=str(exc))
        _pool = None

    return _pool


async def get_pool() -> Optional[redis.Redis]:
    """Return the Redis pool."""

    return _pool


async def close_redis_pool() -> None:
    """Close the Redis pool if it exists."""

    global _pool
    if _pool is None:
        return

    await _pool.close()
    _pool = None
    logger.info("redis_pool_closed")


__all__ = ["init_redis_pool", "close_redis_pool", "get_pool"]
