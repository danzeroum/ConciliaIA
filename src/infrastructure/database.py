"""Lightweight async database helper built on top of asyncpg."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

import asyncpg
import structlog

logger = structlog.get_logger(__name__)


@dataclass(slots=True)
class _DatabaseConfig:
    host: str
    port: int
    user: str
    password: str
    database: str
    min_size: int = 1
    max_size: int = 10


class Database:
    """Async helper for executing raw SQL queries."""

    def __init__(
        self,
        host: str,
        port: int,
        user: str,
        password: str,
        database: str,
        *,
        min_size: int = 1,
        max_size: int = 10,
    ) -> None:
        self._config = _DatabaseConfig(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database,
            min_size=min_size,
            max_size=max_size,
        )
        self._pool: asyncpg.Pool | None = None

    async def connect(self) -> None:
        """Initialise the connection pool."""

        if self._pool is not None:
            return

        self._pool = await asyncpg.create_pool(
            host=self._config.host,
            port=self._config.port,
            user=self._config.user,
            password=self._config.password,
            database=self._config.database,
            min_size=self._config.min_size,
            max_size=self._config.max_size,
        )
        logger.info(
            "database_pool_created",
            host=self._config.host,
            database=self._config.database,
        )

    async def close(self) -> None:
        """Close the connection pool."""

        if self._pool is None:
            return

        await self._pool.close()
        self._pool = None
        logger.info("database_pool_closed")

    async def execute(self, query: str, *args: Any) -> None:
        """Execute a SQL command that does not return rows."""

        pool = await self._ensure_pool()
        async with pool.acquire() as connection:
            await connection.execute(query, *args)

    async def executemany(self, query: str, args_iterable: Iterable[Iterable[Any]]) -> None:
        """Execute the same statement for multiple sets of parameters."""

        pool = await self._ensure_pool()
        async with pool.acquire() as connection:
            await connection.executemany(query, args_iterable)

    async def fetch_one(self, query: str, *args: Any) -> dict[str, Any] | None:
        """Fetch a single row from the database."""

        pool = await self._ensure_pool()
        async with pool.acquire() as connection:
            record = await connection.fetchrow(query, *args)
        if record is None:
            return None
        return dict(record)

    async def fetch_all(self, query: str, *args: Any) -> list[dict[str, Any]]:
        """Fetch multiple rows from the database."""

        pool = await self._ensure_pool()
        async with pool.acquire() as connection:
            records = await connection.fetch(query, *args)
        return [dict(record) for record in records]

    async def _ensure_pool(self) -> asyncpg.Pool:
        if self._pool is None:
            await self.connect()
        if self._pool is None:  # pragma: no cover - defensive
            raise RuntimeError("Database connection pool not initialised")
        return self._pool


__all__ = ["Database"]
