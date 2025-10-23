"""PostgreSQL implementation of SaleRepository."""

from __future__ import annotations

from datetime import date
from typing import List, Optional

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from src.domain.entities import Sale
from src.infrastructure.persistence.repositories import SaleRepository
from ..mappers import SaleMapper
from ..models import SaleModel

logger = structlog.get_logger(__name__)


class PostgreSQLSaleRepository(SaleRepository):
    """PostgreSQL implementation of SaleRepository."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.mapper = SaleMapper()
        self.logger = logger.bind(repository="PostgreSQLSaleRepository")

    async def save(self, sale: Sale) -> None:
        """Save a sale."""
        try:
            stmt = select(SaleModel).where(SaleModel.id == sale.id)
            result = await self.session.execute(stmt)
            existing = result.scalar_one_or_none()

            if existing:
                model = self.mapper.to_model(sale, existing)
            else:
                model = self.mapper.to_model(sale)
                self.session.add(model)

            await self.session.flush()

            self.logger.debug("sale_saved", sale_id=sale.id, tenant_id=sale.tenant_id)

        except Exception as exc:  # pragma: no cover - defensive logging
            self.logger.error("sale_save_failed", sale_id=sale.id, error=str(exc))
            raise

    async def find_by_id(self, tenant_id: str, sale_id: str) -> Optional[Sale]:
        """Find sale by ID."""
        stmt = select(SaleModel).where(
            SaleModel.tenant_id == tenant_id,
            SaleModel.id == sale_id,
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()

        if model:
            return self.mapper.to_entity(model)
        return None

    async def delete(self, tenant_id: str, sale_id: str) -> None:
        """Delete sale by ID for a tenant."""
        stmt = (
            delete(SaleModel)
            .where(
                SaleModel.tenant_id == tenant_id,
                SaleModel.id == sale_id,
            )
            .execution_options(synchronize_session=False)
        )
        await self.session.execute(stmt)

    async def find_by_date_range(self, tenant_id: str, start_date: date, end_date: date) -> List[Sale]:
        """Find sales in date range."""
        stmt = (
            select(SaleModel)
            .where(
                SaleModel.tenant_id == tenant_id,
                SaleModel.date >= start_date,
                SaleModel.date <= end_date,
            )
            .order_by(SaleModel.date, SaleModel.created_at)
        )

        result = await self.session.execute(stmt)
        models = result.scalars().all()

        sales = [self.mapper.to_entity(model) for model in models]

        self.logger.debug(
            "sales_found_by_date_range",
            tenant_id=tenant_id,
            start_date=start_date.isoformat(),
            end_date=end_date.isoformat(),
            count=len(sales),
        )

        return sales

    async def find_unmatched(self, tenant_id: str) -> List[Sale]:
        """Find unmatched sales."""
        stmt = (
            select(SaleModel)
            .where(
                SaleModel.tenant_id == tenant_id,
                ~SaleModel.matches.any(),
            )
            .order_by(SaleModel.date.desc())
        )

        result = await self.session.execute(stmt)
        models = result.scalars().all()

        return [self.mapper.to_entity(model) for model in models]

    async def find_by_nsu(self, tenant_id: str, nsu: str) -> List[Sale]:
        """Find sales by NSU."""
        stmt = select(SaleModel).where(
            SaleModel.tenant_id == tenant_id,
            SaleModel.nsu.ilike(f"%{nsu}%"),
        )

        result = await self.session.execute(stmt)
        models = result.scalars().all()

        return [self.mapper.to_entity(model) for model in models]
