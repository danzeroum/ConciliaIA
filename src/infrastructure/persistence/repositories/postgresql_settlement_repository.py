"""PostgreSQL implementation of SettlementRepository."""

from __future__ import annotations

from datetime import date
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from src.domain.entities import Settlement, SettlementStatus
from src.infrastructure.persistence.repositories import SettlementRepository
from ..mappers import SettlementMapper
from ..models import SettlementModel

logger = structlog.get_logger(__name__)


class PostgreSQLSettlementRepository(SettlementRepository):
    """PostgreSQL implementation of SettlementRepository."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.mapper = SettlementMapper()
        self.logger = logger.bind(repository="PostgreSQLSettlementRepository")

    async def save(self, settlement: Settlement) -> None:
        """Save a settlement."""
        try:
            stmt = select(SettlementModel).where(SettlementModel.id == UUID(settlement.id))
            result = await self.session.execute(stmt)
            existing = result.scalar_one_or_none()

            if existing:
                model = self.mapper.to_model(settlement, existing)
            else:
                model = self.mapper.to_model(settlement)
                self.session.add(model)

            await self.session.flush()

            self.logger.debug("settlement_saved", settlement_id=settlement.id)

        except Exception as exc:  # pragma: no cover - defensive logging
            self.logger.error("settlement_save_failed", settlement_id=settlement.id, error=str(exc))
            raise

    async def find_by_id(self, tenant_id: str, settlement_id: str) -> Optional[Settlement]:
        """Find settlement by ID."""
        stmt = select(SettlementModel).where(
            SettlementModel.tenant_id == UUID(tenant_id),
            SettlementModel.id == UUID(settlement_id),
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()

        if model:
            return self.mapper.to_entity(model)
        return None

    async def find_by_status(self, tenant_id: str, status: SettlementStatus) -> List[Settlement]:
        """Find settlements by status."""
        status_value = status.value if hasattr(status, "value") else status

        stmt = (
            select(SettlementModel)
            .where(
                SettlementModel.tenant_id == UUID(tenant_id),
                SettlementModel.status == status_value,
            )
            .order_by(SettlementModel.expected_date)
        )

        result = await self.session.execute(stmt)
        models = result.scalars().all()

        return [self.mapper.to_entity(model) for model in models]

    async def find_delayed(self, tenant_id: str, reference_date: date | None = None) -> List[Settlement]:
        """Find delayed settlements (expected_date < reference and status pending)."""
        today = reference_date or date.today()

        stmt = (
            select(SettlementModel)
            .where(
                SettlementModel.tenant_id == UUID(tenant_id),
                SettlementModel.status == "pending",
                SettlementModel.expected_date < today,
            )
            .order_by(SettlementModel.expected_date)
        )

        result = await self.session.execute(stmt)
        models = result.scalars().all()

        self.logger.warning("delayed_settlements_found", count=len(models))

        return [self.mapper.to_entity(model) for model in models]

    async def find_by_period(
        self, tenant_id: str, start_date: date, end_date: date
    ) -> List[Settlement]:
        stmt = (
            select(SettlementModel)
            .where(
                SettlementModel.tenant_id == UUID(tenant_id),
                SettlementModel.expected_date >= start_date,
                SettlementModel.expected_date <= end_date,
            )
            .order_by(SettlementModel.expected_date)
        )

        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [self.mapper.to_entity(model) for model in models]
