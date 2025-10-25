"""Utility factories producing scheduler job runners."""

from __future__ import annotations

from collections.abc import Awaitable, Callable

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.services.auto_import_service import AutoImportService
from src.application.services.ingestion_service import IngestionService
from src.domain.entities import ImportSchedule
from src.infrastructure.persistence.repositories.postgresql_transaction_repository import (
    PostgreSQLTransactionRepository,
)

logger = structlog.get_logger(__name__)


SessionFactory = Callable[[], AsyncSession]
Runner = Callable[[ImportSchedule], Awaitable[None]]


def build_auto_import_runner(session_factory: SessionFactory) -> Runner:
    """Create an async callable that runs the auto import service."""

    async def _runner(schedule: ImportSchedule) -> None:
        session: AsyncSession = session_factory()
        try:
            transaction_repo = PostgreSQLTransactionRepository(session)
            ingestion_service = IngestionService(transaction_repo)
            service = AutoImportService(ingestion_service)
            await service.run(schedule)
            await session.commit()
        except Exception:
            await session.rollback()
            logger.exception(
                "auto_import_runner_error",
                schedule_id=schedule.id,
                tenant_id=schedule.tenant_id,
            )
            raise
        finally:
            await session.close()

    return _runner


__all__ = ["build_auto_import_runner"]
