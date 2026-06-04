"""PostgreSQL implementation of DivergenceRepository."""

from __future__ import annotations

from datetime import date, datetime, time
from typing import List, Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from src.domain.entities import Divergence, DivergenceStatus, Severity
from src.infrastructure.persistence.repositories import DivergenceRepository
from ..mappers import DivergenceMapper
from ..models import DivergenceModel

logger = structlog.get_logger(__name__)


class PostgreSQLDivergenceRepository(DivergenceRepository):
    """PostgreSQL implementation of DivergenceRepository."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.mapper = DivergenceMapper()
        self.logger = logger.bind(repository="PostgreSQLDivergenceRepository")

    async def save(self, divergence: Divergence) -> None:
        """Save a divergence."""
        try:
            stmt = select(DivergenceModel).where(DivergenceModel.id == divergence.id)
            result = await self.session.execute(stmt)
            existing = result.scalar_one_or_none()

            if existing:
                model = self.mapper.to_model(divergence, existing)
            else:
                model = self.mapper.to_model(divergence)
                self.session.add(model)

            await self.session.flush()

            self.logger.debug(
                "divergence_saved",
                divergence_id=divergence.id,
                severity=getattr(divergence.severity, "value", divergence.severity),
            )

        except Exception as exc:  # pragma: no cover - defensive logging
            self.logger.error("divergence_save_failed", divergence_id=divergence.id, error=str(exc))
            raise

    async def find_by_id(self, tenant_id: str, divergence_id: str) -> Optional[Divergence]:
        """Find divergence by ID."""
        stmt = select(DivergenceModel).where(
            DivergenceModel.tenant_id == tenant_id,
            DivergenceModel.id == divergence_id,
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()

        if model:
            return self.mapper.to_entity(model)
        return None

    async def find_by_status(self, tenant_id: str, status: DivergenceStatus) -> List[Divergence]:
        """Find divergences by status."""
        status_value = status.value if hasattr(status, "value") else status

        stmt = (
            select(DivergenceModel)
            .where(
                DivergenceModel.tenant_id == tenant_id,
                DivergenceModel.status == status_value,
            )
            .order_by(DivergenceModel.severity.desc(), DivergenceModel.detected_at.desc())
        )

        result = await self.session.execute(stmt)
        models = result.scalars().all()

        return [self.mapper.to_entity(model) for model in models]

    async def find_by_severity(self, tenant_id: str, severity: Severity) -> List[Divergence]:
        """Find divergences by severity."""
        severity_value = severity.value if hasattr(severity, "value") else severity

        stmt = (
            select(DivergenceModel)
            .where(
                DivergenceModel.tenant_id == tenant_id,
                DivergenceModel.severity == severity_value,
            )
            .order_by(DivergenceModel.detected_at.desc())
        )

        result = await self.session.execute(stmt)
        models = result.scalars().all()

        return [self.mapper.to_entity(model) for model in models]

    async def find_critical_open(self, tenant_id: str) -> List[Divergence]:
        """Find critical open divergences."""
        stmt = (
            select(DivergenceModel)
            .where(
                DivergenceModel.tenant_id == tenant_id,
                DivergenceModel.severity == "critical",
                DivergenceModel.status == "open",
            )
            .order_by(DivergenceModel.detected_at.desc())
        )

        result = await self.session.execute(stmt)
        models = result.scalars().all()

        self.logger.warning("critical_divergences_found", count=len(models))

        return [self.mapper.to_entity(model) for model in models]

    async def find_paginated(
        self,
        tenant_id: str,
        *,
        status: Optional[DivergenceStatus] = None,
        divergence_type: Optional[str] = None,
        severity: Optional[Severity] = None,
        page: int = 1,
        page_size: int = 50,
    ) -> tuple[List[Divergence], int]:
        """Return a page of divergences and the total count for the filters."""
        filters = [DivergenceModel.tenant_id == tenant_id]

        if status is not None:
            filters.append(
                DivergenceModel.status == (status.value if hasattr(status, "value") else status)
            )
        if divergence_type is not None:
            filters.append(DivergenceModel.divergence_type == divergence_type)
        if severity is not None:
            filters.append(
                DivergenceModel.severity
                == (severity.value if hasattr(severity, "value") else severity)
            )

        count_stmt = select(func.count()).select_from(DivergenceModel).where(*filters)
        total = (await self.session.execute(count_stmt)).scalar_one()

        page = max(page, 1)
        page_size = max(min(page_size, 200), 1)

        stmt = (
            select(DivergenceModel)
            .where(*filters)
            .order_by(DivergenceModel.detected_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )

        result = await self.session.execute(stmt)
        models = result.scalars().all()

        return [self.mapper.to_entity(model) for model in models], int(total)

    async def find_by_date_range(
        self, tenant_id: str, start_date: date, end_date: date
    ) -> List[Divergence]:
        """Find divergences detected within a date interval."""
        start_dt = datetime.combine(start_date, time.min)
        end_dt = datetime.combine(end_date, time.max)

        stmt = (
            select(DivergenceModel)
            .where(
                DivergenceModel.tenant_id == tenant_id,
                DivergenceModel.detected_at >= start_dt,
                DivergenceModel.detected_at <= end_dt,
            )
            .order_by(DivergenceModel.detected_at)
        )

        result = await self.session.execute(stmt)
        models = result.scalars().all()

        return [self.mapper.to_entity(model) for model in models]
