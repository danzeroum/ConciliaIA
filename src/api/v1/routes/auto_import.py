"""Endpoints controlling automatic acquirer imports."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import (
    get_auto_import_scheduler,
    get_current_tenant,
    get_db_session,
)
from src.domain.entities import ImportSchedule, Tenant
from src.infrastructure.persistence.repositories.postgresql_import_schedule_repository import (
    PostgreSQLImportScheduleRepository,
)

router = APIRouter(prefix="/auto-import", tags=["Auto Import"])


class ScheduleRequest(BaseModel):
    acquirer: str = Field(default="cielo", description="Acquirer identifier")
    schedule_type: str = Field(..., description="daily, weekly or monthly")
    time_of_day: str = Field(..., pattern=r"^\d{2}:\d{2}$", description="HH:MM 24h")
    days_to_import: int = Field(1, ge=1, le=31)
    credential_hint: Optional[str] = Field(None, description="Human friendly credential hint")
    webhook_url: Optional[str] = None


class ScheduleResponse(BaseModel):
    id: str
    acquirer: str
    schedule_type: str
    time_of_day: str
    days_to_import: int
    is_active: bool
    last_run_at: Optional[datetime]
    next_run_at: Optional[datetime]
    webhook_url: Optional[str] = None


@router.post("/schedule", response_model=ScheduleResponse, status_code=status.HTTP_201_CREATED)
async def create_schedule(
    request: ScheduleRequest,
    tenant: Tenant = Depends(get_current_tenant),
    session: AsyncSession = Depends(get_db_session),
    scheduler=Depends(get_auto_import_scheduler),
):
    repository = PostgreSQLImportScheduleRepository(session)

    existing = await repository.get_by_tenant(tenant.id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Já existe um agendamento ativo para este tenant. Atualize-o em vez de criar outro.",
        )

    schedule = ImportSchedule.create(
        tenant_id=tenant.id,
        acquirer=request.acquirer,
        schedule_type=request.schedule_type,
        time_of_day=request.time_of_day,
        days_to_import=request.days_to_import,
        credential_hint=request.credential_hint,
        webhook_url=request.webhook_url,
    )

    await scheduler.register(schedule)

    return ScheduleResponse(
        id=schedule.id,
        acquirer=schedule.acquirer,
        schedule_type=schedule.schedule_type,
        time_of_day=schedule.time_of_day,
        days_to_import=schedule.days_to_import,
        is_active=schedule.is_active,
        last_run_at=schedule.last_run_at,
        next_run_at=schedule.next_run_at,
        webhook_url=schedule.webhook_url,
    )


@router.put("/schedule/{schedule_id}", response_model=ScheduleResponse)
async def update_schedule(
    schedule_id: str,
    request: ScheduleRequest,
    tenant: Tenant = Depends(get_current_tenant),
    session: AsyncSession = Depends(get_db_session),
    scheduler=Depends(get_auto_import_scheduler),
):
    repository = PostgreSQLImportScheduleRepository(session)
    schedule = await repository.get_by_id(schedule_id)
    if schedule is None or schedule.tenant_id != tenant.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agendamento não encontrado")

    schedule.schedule_type = request.schedule_type
    schedule.time_of_day = request.time_of_day
    schedule.days_to_import = request.days_to_import
    schedule.credential_hint = request.credential_hint
    schedule.webhook_url = request.webhook_url

    await scheduler.update(schedule)

    return ScheduleResponse(
        id=schedule.id,
        acquirer=schedule.acquirer,
        schedule_type=schedule.schedule_type,
        time_of_day=schedule.time_of_day,
        days_to_import=schedule.days_to_import,
        is_active=schedule.is_active,
        last_run_at=schedule.last_run_at,
        next_run_at=schedule.next_run_at,
        webhook_url=schedule.webhook_url,
    )


@router.delete("/schedule/{schedule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_schedule(
    schedule_id: str,
    tenant: Tenant = Depends(get_current_tenant),
    session: AsyncSession = Depends(get_db_session),
    scheduler=Depends(get_auto_import_scheduler),
):
    repository = PostgreSQLImportScheduleRepository(session)
    schedule = await repository.get_by_id(schedule_id)
    if schedule is None or schedule.tenant_id != tenant.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agendamento não encontrado")

    await scheduler.deactivate(schedule_id)
    return None


@router.delete("/schedule", status_code=status.HTTP_204_NO_CONTENT)
async def delete_current_schedule(
    tenant: Tenant = Depends(get_current_tenant),
    session: AsyncSession = Depends(get_db_session),
    scheduler=Depends(get_auto_import_scheduler),
):
    repository = PostgreSQLImportScheduleRepository(session)
    schedules = await repository.get_by_tenant(tenant.id)
    for schedule in schedules:
        await scheduler.deactivate(schedule.id)
    return None


@router.get("/schedule", response_model=list[ScheduleResponse])
async def list_schedules(
    tenant: Tenant = Depends(get_current_tenant),
    session: AsyncSession = Depends(get_db_session),
):
    repository = PostgreSQLImportScheduleRepository(session)
    schedules = await repository.get_by_tenant(tenant.id)
    return [
        ScheduleResponse(
            id=s.id,
            acquirer=s.acquirer,
            schedule_type=s.schedule_type,
            time_of_day=s.time_of_day,
            days_to_import=s.days_to_import,
            is_active=s.is_active,
            last_run_at=s.last_run_at,
            next_run_at=s.next_run_at,
            webhook_url=s.webhook_url,
        )
        for s in schedules
    ]


__all__ = ["router"]
