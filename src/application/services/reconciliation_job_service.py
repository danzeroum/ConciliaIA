"""Asynchronous reconciliation jobs.

Implements the "job table + lightweight in-process worker" approach: a request
creates a job row (status ``pending``) and returns immediately with ``202`` and
the ``job_id``; an ``asyncio`` task then runs the reconciliation use case using
its own database session, recording lifecycle checkpoints and the final result
so callers can poll ``GET /reconciliation-jobs/{id}/status``.

This deliberately avoids a heavyweight broker (Celery/Kafka/BPMS). Those remain
a backlog item to adopt only when process metrics justify the complexity.
"""

from __future__ import annotations

import asyncio
from datetime import date, datetime
from typing import Any, Optional
from uuid import uuid4

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker

from src.infrastructure.persistence.models import ReconciliationJobModel

logger = structlog.get_logger(__name__)


class JobStatus:
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class ReconciliationJobService:
    """Create, run and inspect asynchronous reconciliation jobs."""

    def __init__(
        self,
        session_factory: async_sessionmaker,
        use_case_builder,
    ) -> None:
        # ``use_case_builder`` is a callable(session) -> ReconcileTransactionsUseCase
        # (``dependencies.build_reconciliation_use_case``), injected to avoid a
        # circular import between the API and application layers.
        self._session_factory = session_factory
        self._build_use_case = use_case_builder
        self._tasks: set[asyncio.Task] = set()
        self.logger = logger.bind(service="ReconciliationJobService")

    async def create_job(
        self, tenant_id: str, start_date: date, end_date: date
    ) -> dict[str, Any]:
        """Persist a pending job and launch its background execution."""
        job_id = str(uuid4())
        async with self._session_factory() as session:
            session.add(
                ReconciliationJobModel(
                    id=job_id,
                    tenant_id=tenant_id,
                    status=JobStatus.PENDING,
                    start_date=start_date,
                    end_date=end_date,
                    checkpoints={"phase": "queued", "percent": 0},
                )
            )
            await session.commit()

        task = asyncio.create_task(
            self._execute(job_id, tenant_id, start_date, end_date)
        )
        # Keep a reference so the task is not garbage collected mid-flight.
        self._tasks.add(task)
        task.add_done_callback(self._tasks.discard)

        self.logger.info("reconciliation_job_created", job_id=job_id, tenant_id=tenant_id)
        return {"job_id": job_id, "status": JobStatus.PENDING}

    async def _execute(
        self, job_id: str, tenant_id: str, start_date: date, end_date: date
    ) -> None:
        async with self._session_factory() as session:
            try:
                await self._set_running(session, job_id)

                use_case = self._build_use_case(session)
                result = await use_case.execute(
                    tenant_id=tenant_id,
                    start_date=start_date,
                    end_date=end_date,
                )

                payload = {
                    "matched": result.matched_count,
                    "divergences": len(result.divergences),
                    "accuracy": float(result.accuracy * 100),
                    "precision": float(result.precision * 100),
                    "recall": float(result.recall * 100),
                }
                await self._set_completed(session, job_id, payload)
                self.logger.info("reconciliation_job_completed", job_id=job_id, **payload)
            except Exception as exc:  # pragma: no cover - defensive
                await session.rollback()
                await self._set_failed(session, job_id, str(exc))
                self.logger.error(
                    "reconciliation_job_failed", job_id=job_id, error=str(exc)
                )

    async def _set_running(self, session, job_id: str) -> None:
        job = await session.get(ReconciliationJobModel, job_id)
        if job is None:
            return
        job.status = JobStatus.RUNNING
        job.started_at = datetime.utcnow()
        job.checkpoints = {"phase": "matching", "percent": 10}
        await session.commit()

    async def _set_completed(self, session, job_id: str, payload: dict[str, Any]) -> None:
        job = await session.get(ReconciliationJobModel, job_id)
        if job is None:
            return
        job.status = JobStatus.COMPLETED
        job.result = payload
        job.checkpoints = {"phase": "done", "percent": 100}
        job.finished_at = datetime.utcnow()
        await session.commit()

    async def _set_failed(self, session, job_id: str, error: str) -> None:
        job = await session.get(ReconciliationJobModel, job_id)
        if job is None:
            return
        job.status = JobStatus.FAILED
        job.error = error
        job.checkpoints = {"phase": "failed", "percent": 100}
        job.finished_at = datetime.utcnow()
        await session.commit()

    async def get_job(self, tenant_id: str, job_id: str) -> Optional[dict[str, Any]]:
        async with self._session_factory() as session:
            job = await session.get(ReconciliationJobModel, job_id)
            if job is None or str(job.tenant_id) != tenant_id:
                return None
            return self._to_dict(job)

    async def list_jobs(self, tenant_id: str, limit: int = 20) -> list[dict[str, Any]]:
        async with self._session_factory() as session:
            stmt = (
                select(ReconciliationJobModel)
                .where(ReconciliationJobModel.tenant_id == tenant_id)
                .order_by(ReconciliationJobModel.created_at.desc())
                .limit(limit)
            )
            rows = (await session.execute(stmt)).scalars().all()
            return [self._to_dict(job) for job in rows]

    @staticmethod
    def _to_dict(job: ReconciliationJobModel) -> dict[str, Any]:
        return {
            "job_id": str(job.id),
            "tenant_id": str(job.tenant_id),
            "status": job.status,
            "start_date": job.start_date.isoformat() if job.start_date else None,
            "end_date": job.end_date.isoformat() if job.end_date else None,
            "checkpoints": job.checkpoints or {},
            "result": job.result,
            "error": job.error,
            "created_at": job.created_at.isoformat() if job.created_at else None,
            "started_at": job.started_at.isoformat() if job.started_at else None,
            "finished_at": job.finished_at.isoformat() if job.finished_at else None,
        }


__all__ = ["ReconciliationJobService", "JobStatus"]
