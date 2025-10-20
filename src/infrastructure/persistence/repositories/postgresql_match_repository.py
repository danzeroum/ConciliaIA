"""PostgreSQL implementation of MatchRepository."""

from __future__ import annotations

from datetime import date, datetime, time
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from src.domain.entities import ReconciliationMatch
from src.infrastructure.persistence.repositories import MatchRepository
from ..mappers import MatchMapper
from ..models import MatchModel

logger = structlog.get_logger(__name__)


class PostgreSQLMatchRepository(MatchRepository):
    """PostgreSQL implementation of MatchRepository."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.mapper = MatchMapper()
        self.logger = logger.bind(repository="PostgreSQLMatchRepository")

    async def save(self, match: ReconciliationMatch) -> None:
        """Save a match."""
        try:
            stmt = select(MatchModel).where(MatchModel.id == UUID(match.id))
            result = await self.session.execute(stmt)
            existing = result.scalar_one_or_none()

            if existing:
                model = self.mapper.to_model(match, existing)
            else:
                model = self.mapper.to_model(match)
                self.session.add(model)

            await self.session.flush()

            self.logger.debug("match_saved", match_id=match.id)

        except Exception as exc:  # pragma: no cover - defensive logging
            self.logger.error("match_save_failed", match_id=match.id, error=str(exc))
            raise

    async def find_by_id(self, tenant_id: str, match_id: str) -> Optional[ReconciliationMatch]:
        """Find match by ID."""
        stmt = select(MatchModel).where(
            MatchModel.tenant_id == UUID(tenant_id),
            MatchModel.id == UUID(match_id),
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()

        if model:
            return self.mapper.to_entity(model)
        return None

    async def find_by_sale(self, tenant_id: str, sale_id: str) -> List[ReconciliationMatch]:
        """Find matches for a sale."""
        stmt = (
            select(MatchModel)
            .where(
                MatchModel.tenant_id == UUID(tenant_id),
                MatchModel.sale_id == UUID(sale_id),
            )
            .order_by(MatchModel.matched_at.desc())
        )

        result = await self.session.execute(stmt)
        models = result.scalars().all()

        return [self.mapper.to_entity(model) for model in models]

    async def find_by_transaction(self, tenant_id: str, transaction_id: str) -> List[ReconciliationMatch]:
        """Find matches for a transaction."""
        stmt = (
            select(MatchModel)
            .where(
                MatchModel.tenant_id == UUID(tenant_id),
                MatchModel.transaction_id == UUID(transaction_id),
            )
            .order_by(MatchModel.matched_at.desc())
        )

        result = await self.session.execute(stmt)
        models = result.scalars().all()

        return [self.mapper.to_entity(model) for model in models]

    async def find_requiring_review(self, tenant_id: str) -> List[ReconciliationMatch]:
        """Find matches requiring human review (confidence < 0.95)."""
        stmt = (
            select(MatchModel)
            .where(
                MatchModel.tenant_id == UUID(tenant_id),
                MatchModel.validated.is_(False),
                MatchModel.confidence < 0.95,
            )
            .order_by(MatchModel.confidence.asc(), MatchModel.matched_at.desc())
        )

        result = await self.session.execute(stmt)
        models = result.scalars().all()

        self.logger.info("matches_requiring_review", count=len(models))

        return [self.mapper.to_entity(model) for model in models]

    async def find_by_date_range(
        self, tenant_id: str, start_date: date, end_date: date
    ) -> List[ReconciliationMatch]:
        """Find matches created within a date range."""
        start_dt = datetime.combine(start_date, time.min)
        end_dt = datetime.combine(end_date, time.max)

        stmt = (
            select(MatchModel)
            .where(
                MatchModel.tenant_id == UUID(tenant_id),
                MatchModel.matched_at >= start_dt,
                MatchModel.matched_at <= end_dt,
            )
            .order_by(MatchModel.matched_at)
        )

        result = await self.session.execute(stmt)
        models = result.scalars().all()

        return [self.mapper.to_entity(model) for model in models]
