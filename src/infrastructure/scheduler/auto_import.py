"""Async scheduler responsible for recurring acquirer imports."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Dict, Iterable

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities import ImportSchedule
from src.infrastructure.persistence.repositories.postgresql_import_schedule_repository import (
    PostgreSQLImportScheduleRepository,
)

logger = structlog.get_logger(__name__)


RunnerType = Callable[[ImportSchedule], Awaitable[None]]
SessionFactory = Callable[[], AsyncSession]


class AutoImportScheduler:
    """Manage background jobs for automatic acquirer imports."""

    def __init__(
        self,
        *,
        session_factory: SessionFactory,
        runner: RunnerType,
    ) -> None:
        self._session_factory = session_factory
        self._runner = runner
        self._scheduler = AsyncIOScheduler()
        self._jobs: Dict[str, str] = {}
        self._logger = logger.bind(component="AutoImportScheduler")

    def start(self) -> None:
        if not self._scheduler.running:
            self._scheduler.start()
            self._logger.info("auto_import_scheduler_started")

    def shutdown(self) -> None:
        if self._scheduler.running:
            self._scheduler.shutdown(wait=False)
            self._logger.info("auto_import_scheduler_stopped")

    async def initialise(self) -> None:
        """Load schedules from the database and ensure jobs are registered."""
        schedules = await self._load_active_schedules()
        for schedule in schedules:
            self._upsert_job(schedule)
        self._logger.info("auto_import_scheduler_initialised", count=len(schedules))

    async def register(self, schedule: ImportSchedule) -> None:
        """Persist and register a new schedule."""
        async with self._session_scope() as (session, repository):
            await repository.add(schedule)
            await session.commit()
        self._upsert_job(schedule)

    async def update(self, schedule: ImportSchedule) -> None:
        async with self._session_scope() as (session, repository):
            await repository.update(schedule)
            await session.commit()
        self._upsert_job(schedule)

    async def deactivate(self, schedule_id: str) -> None:
        async with self._session_scope() as (session, repository):
            schedule = await repository.get_by_id(schedule_id)
            if not schedule:
                return
            schedule.deactivate()
            await repository.update(schedule)
            await session.commit()

        job_id = self._jobs.pop(schedule_id, None)
        if job_id:
            self._scheduler.remove_job(job_id)
            self._logger.info("auto_import_job_removed", schedule_id=schedule_id)

    async def _load_active_schedules(self) -> Iterable[ImportSchedule]:
        async with self._session_scope() as (_session, repository):
            schedules = await repository.list_active()
        return schedules

    def _upsert_job(self, schedule: ImportSchedule) -> None:
        if not schedule.is_active:
            return

        trigger = self._build_trigger(schedule)
        job_id = f"auto-import::{schedule.id}"

        existing_job = self._scheduler.get_job(job_id)
        if existing_job:
            self._scheduler.remove_job(job_id)

        self._scheduler.add_job(
            self._execute_job,
            trigger=trigger,
            id=job_id,
            name=schedule.display_name,
            args=[schedule.id],
            replace_existing=True,
        )
        self._jobs[schedule.id] = job_id
        self._logger.info(
            "auto_import_job_registered",
            schedule_id=schedule.id,
            trigger=str(trigger),
        )

    def _build_trigger(self, schedule: ImportSchedule) -> CronTrigger:
        hour, minute = (int(part) for part in schedule.time_of_day.split(":", maxsplit=1))
        if schedule.schedule_type == "daily":
            return CronTrigger(hour=hour, minute=minute)
        if schedule.schedule_type == "weekly":
            return CronTrigger(day_of_week="mon", hour=hour, minute=minute)
        if schedule.schedule_type == "monthly":
            return CronTrigger(day="1", hour=hour, minute=minute)
        raise ValueError(f"Unsupported schedule type: {schedule.schedule_type}")

    async def _execute_job(self, schedule_id: str) -> None:
        async with self._session_scope() as (session, repository):
            schedule = await repository.get_by_id(schedule_id)
            if not schedule or not schedule.is_active:
                self._logger.info(
                    "auto_import_job_skipped",
                    schedule_id=schedule_id,
                    reason="inactive",
                )
                return

            try:
                await self._runner(schedule)
                schedule.mark_success(datetime.utcnow())
                await repository.update(schedule)
                await session.commit()
                self._logger.info(
                    "auto_import_job_completed",
                    schedule_id=schedule_id,
                )
            except Exception as exc:  # pragma: no cover - defensive logging
                await session.rollback()
                schedule.mark_failure()
                async with self._session_scope() as (inner_session, inner_repo):
                    await inner_repo.update(schedule)
                    await inner_session.commit()
                self._logger.error(
                    "auto_import_job_failed",
                    schedule_id=schedule_id,
                    error=str(exc),
                )

    @asynccontextmanager
    async def _session_scope(self):
        session: AsyncSession = self._session_factory()
        repository = PostgreSQLImportScheduleRepository(session)
        try:
            yield session, repository
        finally:
            await session.close()
