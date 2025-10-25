"""Service orchestrating automatic imports triggered by the scheduler."""

from __future__ import annotations

from datetime import date, timedelta

import structlog

from src.application.services.ingestion_service import IngestionService
from src.domain.entities import ImportSchedule

logger = structlog.get_logger(__name__)


class AutoImportService:
    """High-level coordinator for recurring acquirer imports."""

    def __init__(self, ingestion_service: IngestionService) -> None:
        self._ingestion_service = ingestion_service
        self._logger = logger.bind(service="AutoImportService")

    async def run(self, schedule: ImportSchedule) -> None:
        """Execute the import routine associated with the schedule."""

        target_end = date.today() - timedelta(days=1)
        target_start = target_end - timedelta(days=schedule.days_to_import - 1)

        self._logger.info(
            "auto_import_run_started",
            tenant_id=schedule.tenant_id,
            acquirer=schedule.acquirer,
            start_date=target_start.isoformat(),
            end_date=target_end.isoformat(),
        )

        # For the MVP we focus on Cielo, leveraging existing ingestion service support
        if schedule.acquirer.lower() != "cielo":
            self._logger.warning(
                "auto_import_unsupported_acquirer",
                acquirer=schedule.acquirer,
                schedule_id=schedule.id,
            )
            return

        await self._ingestion_service.ingest_all_acquirers(
            tenant_id=schedule.tenant_id,
            start_date=target_start,
            end_date=target_end,
            acquirer_configs={
                "cielo": {"client_params": {}},
            },
        )

        self._logger.info(
            "auto_import_run_completed",
            tenant_id=schedule.tenant_id,
            schedule_id=schedule.id,
        )


__all__ = ["AutoImportService"]
