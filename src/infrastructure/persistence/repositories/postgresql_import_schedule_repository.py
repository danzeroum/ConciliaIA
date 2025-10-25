"""PostgreSQL implementation for ImportScheduleRepository."""

from __future__ import annotations

from typing import Iterable, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from src.domain.entities import ImportSchedule
from src.domain.repositories import ImportScheduleRepository
from ..mappers import ImportScheduleMapper
from ..models import ImportScheduleModel

logger = structlog.get_logger(__name__)


class PostgreSQLImportScheduleRepository(ImportScheduleRepository):
    """Persist import schedules using SQLAlchemy models."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.mapper = ImportScheduleMapper()
        self.logger = logger.bind(repository="PostgreSQLImportScheduleRepository")

    async def add(self, schedule: ImportSchedule) -> None:
        model = self.mapper.to_model(schedule)
        self.session.add(model)
        self.logger.info(
            "import_schedule_added",
            schedule_id=schedule.id,
            tenant_id=schedule.tenant_id,
        )

    async def update(self, schedule: ImportSchedule) -> None:
        stmt = select(ImportScheduleModel).where(
            ImportScheduleModel.id == UUID(schedule.id)
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is None:
            raise ValueError(f"Schedule {schedule.id} not found")

        self.mapper.to_model(schedule, model)
        self.logger.info(
            "import_schedule_updated",
            schedule_id=schedule.id,
            tenant_id=schedule.tenant_id,
        )

    async def get_by_id(self, schedule_id: str) -> Optional[ImportSchedule]:
        stmt = select(ImportScheduleModel).where(
            ImportScheduleModel.id == UUID(schedule_id)
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return self.mapper.to_entity(model) if model else None

    async def get_by_tenant(self, tenant_id: str) -> Iterable[ImportSchedule]:
        stmt = select(ImportScheduleModel).where(
            ImportScheduleModel.tenant_id == UUID(tenant_id)
        )
        result = await self.session.execute(stmt)
        return [self.mapper.to_entity(model) for model in result.scalars().all()]

    async def list_active(self) -> Iterable[ImportSchedule]:
        stmt = select(ImportScheduleModel).where(ImportScheduleModel.is_active.is_(True))
        result = await self.session.execute(stmt)
        return [self.mapper.to_entity(model) for model in result.scalars().all()]


__all__ = ["PostgreSQLImportScheduleRepository"]
