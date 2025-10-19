"""Database connection and session management."""

from __future__ import annotations

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base
import structlog

logger = structlog.get_logger(__name__)

Base = declarative_base()


class Database:
    """Database connection manager."""

    def __init__(self, database_url: str):
        """Initialize database connection."""
        self.engine = create_async_engine(
            database_url,
            echo=False,
            pool_size=20,
            max_overflow=40,
            pool_pre_ping=True,
            pool_recycle=3600,
        )
        self.session_factory = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )
        logger.info("database_initialized", url=database_url.split("@")[0])

    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get database session."""
        async with self.session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()

    async def close(self) -> None:
        """Close database connections."""
        await self.engine.dispose()
        logger.info("database_closed")
