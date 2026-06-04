"""Asynchronous reconciliation jobs and process metrics."""

from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import (
    get_current_tenant,
    get_db_session,
    get_reconciliation_job_service,
)
from src.application.services.reconciliation_job_service import (
    JobStatus,
    ReconciliationJobService,
)
from src.domain.entities import Tenant
from src.infrastructure.persistence.models import (
    DivergenceModel,
    MatchModel,
    ReconciliationJobModel,
)

router = APIRouter()


class ReconciliationJobRequest(BaseModel):
    """Request payload for launching an asynchronous reconciliation."""

    start_date: date = Field(..., description="Start date (YYYY-MM-DD)")
    end_date: date = Field(..., description="End date (YYYY-MM-DD)")


class ReconciliationJobAccepted(BaseModel):
    """Response returned immediately when a job is accepted (202)."""

    job_id: str
    status: str


class ReconciliationJobStatus(BaseModel):
    """Full job state used for polling."""

    job_id: str
    tenant_id: str
    status: str
    start_date: Optional[str]
    end_date: Optional[str]
    checkpoints: dict
    result: Optional[dict]
    error: Optional[str]
    created_at: Optional[str]
    started_at: Optional[str]
    finished_at: Optional[str]


class ProcessMetrics(BaseModel):
    """Reconciliation process metrics that inform scaling decisions."""

    completed_jobs: int
    failed_jobs: int
    pending_jobs: int
    duration_p50_seconds: Optional[float]
    duration_p95_seconds: Optional[float]
    matches_last_30d: int
    divergence_backlog: int
    auto_approval_rate: Optional[float]


def _percentile(values: List[float], pct: float) -> Optional[float]:
    """Nearest-rank percentile of a list of values."""
    if not values:
        return None
    ordered = sorted(values)
    k = max(0, min(len(ordered) - 1, int(round((pct / 100.0) * len(ordered) + 0.5)) - 1))
    return round(ordered[k], 3)


@router.post(
    "/reconciliation-jobs",
    response_model=ReconciliationJobAccepted,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Launch an asynchronous reconciliation",
    tags=["Reconciliation"],
)
async def create_reconciliation_job(
    request: ReconciliationJobRequest,
    tenant: Tenant = Depends(get_current_tenant),
    service: ReconciliationJobService = Depends(get_reconciliation_job_service),
) -> ReconciliationJobAccepted:
    """Accept a reconciliation request and process it in the background."""
    if request.start_date > request.end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="start_date must be <= end_date",
        )
    if (request.end_date - request.start_date).days > 90:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Date range cannot exceed 90 days",
        )

    job = await service.create_job(tenant.id, request.start_date, request.end_date)
    return ReconciliationJobAccepted(**job)


@router.get(
    "/reconciliation-jobs",
    response_model=List[ReconciliationJobStatus],
    summary="List recent reconciliation jobs",
    tags=["Reconciliation"],
)
async def list_reconciliation_jobs(
    tenant: Tenant = Depends(get_current_tenant),
    service: ReconciliationJobService = Depends(get_reconciliation_job_service),
    limit: int = Query(20, ge=1, le=100),
) -> List[ReconciliationJobStatus]:
    jobs = await service.list_jobs(tenant.id, limit=limit)
    return [ReconciliationJobStatus(**job) for job in jobs]


@router.get(
    "/reconciliation-jobs/metrics",
    response_model=ProcessMetrics,
    summary="Reconciliation process metrics",
    tags=["Reconciliation"],
)
async def reconciliation_metrics(
    tenant: Tenant = Depends(get_current_tenant),
    session: AsyncSession = Depends(get_db_session),
) -> ProcessMetrics:
    """Aggregate process metrics: throughput, backlog, latency and auto-approval."""
    tenant_id = tenant.id

    async def _count(stmt) -> int:
        return int((await session.execute(stmt)).scalar_one())

    completed = await _count(
        select(func.count())
        .select_from(ReconciliationJobModel)
        .where(
            ReconciliationJobModel.tenant_id == tenant_id,
            ReconciliationJobModel.status == JobStatus.COMPLETED,
        )
    )
    failed = await _count(
        select(func.count())
        .select_from(ReconciliationJobModel)
        .where(
            ReconciliationJobModel.tenant_id == tenant_id,
            ReconciliationJobModel.status == JobStatus.FAILED,
        )
    )
    pending = await _count(
        select(func.count())
        .select_from(ReconciliationJobModel)
        .where(
            ReconciliationJobModel.tenant_id == tenant_id,
            ReconciliationJobModel.status.in_([JobStatus.PENDING, JobStatus.RUNNING]),
        )
    )

    # Durations of completed jobs (seconds).
    duration_rows = (
        await session.execute(
            select(
                ReconciliationJobModel.started_at,
                ReconciliationJobModel.finished_at,
            ).where(
                ReconciliationJobModel.tenant_id == tenant_id,
                ReconciliationJobModel.status == JobStatus.COMPLETED,
                ReconciliationJobModel.started_at.is_not(None),
                ReconciliationJobModel.finished_at.is_not(None),
            )
        )
    ).all()
    durations = [
        (finished - started).total_seconds()
        for started, finished in duration_rows
        if started and finished
    ]

    since = datetime.utcnow() - timedelta(days=30)
    matches_last_30d = await _count(
        select(func.count())
        .select_from(MatchModel)
        .where(MatchModel.tenant_id == tenant_id, MatchModel.matched_at >= since)
    )

    divergence_backlog = await _count(
        select(func.count())
        .select_from(DivergenceModel)
        .where(DivergenceModel.tenant_id == tenant_id, DivergenceModel.status == "open")
    )

    total_matches = await _count(
        select(func.count())
        .select_from(MatchModel)
        .where(MatchModel.tenant_id == tenant_id)
    )
    auto_approved = await _count(
        select(func.count())
        .select_from(MatchModel)
        .where(MatchModel.tenant_id == tenant_id, MatchModel.validated_by == "system")
    )
    auto_approval_rate = (
        round(auto_approved / total_matches, 4) if total_matches else None
    )

    return ProcessMetrics(
        completed_jobs=completed,
        failed_jobs=failed,
        pending_jobs=pending,
        duration_p50_seconds=_percentile(durations, 50),
        duration_p95_seconds=_percentile(durations, 95),
        matches_last_30d=matches_last_30d,
        divergence_backlog=divergence_backlog,
        auto_approval_rate=auto_approval_rate,
    )


@router.get(
    "/reconciliation-jobs/{job_id}/status",
    response_model=ReconciliationJobStatus,
    summary="Poll reconciliation job status",
    tags=["Reconciliation"],
)
async def get_reconciliation_job_status(
    job_id: str,
    tenant: Tenant = Depends(get_current_tenant),
    service: ReconciliationJobService = Depends(get_reconciliation_job_service),
) -> ReconciliationJobStatus:
    job = await service.get_job(tenant.id, job_id)
    if job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Reconciliation job not found"
        )
    return ReconciliationJobStatus(**job)


__all__ = ["router"]
