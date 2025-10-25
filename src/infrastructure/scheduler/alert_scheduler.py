"""APScheduler job to run proactive alert checks."""

from __future__ import annotations

from typing import Iterable

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import structlog

from src.infrastructure.alerts import ProactiveAlertEngine

logger = structlog.get_logger(__name__)


class AlertScheduler:
    """Configure recurring executions of the proactive alert engine."""

    def __init__(self, alert_engine: ProactiveAlertEngine) -> None:
        self._alert_engine = alert_engine
        self._scheduler = AsyncIOScheduler()

    def schedule_daily_checks(self, tenant_ids: Iterable[str]) -> None:
        """Schedule the alert checks once per day at 09:00 for each tenant."""

        tenant_list = list(tenant_ids)

        for tenant_id in tenant_list:
            job_id = f"alert_check_{tenant_id}"
            self._scheduler.add_job(
                func=self._run_checks,
                trigger=CronTrigger(hour=9, minute=0),
                args=[tenant_id],
                id=job_id,
                name=f"Proactive alerts - {tenant_id}",
                replace_existing=True,
            )

        logger.info(
            "alert_scheduler.jobs_scheduled",
            tenants=len(tenant_list),
        )

    async def _run_checks(self, tenant_id: str) -> None:
        try:
            await self._alert_engine.run_all_checks(tenant_id)
        except Exception as exc:  # pragma: no cover - defensive logging
            logger.exception("alert_scheduler.job_error", tenant_id=tenant_id, error=str(exc))

    def start(self) -> None:
        if not self._scheduler.running:
            self._scheduler.start()
            logger.info("alert_scheduler.started")

    def stop(self) -> None:
        if self._scheduler.running:
            self._scheduler.shutdown()
            logger.info("alert_scheduler.stopped")


__all__ = ["AlertScheduler"]
