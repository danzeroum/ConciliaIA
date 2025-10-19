"""PostgreSQL implementation of TransactionRepository."""

from __future__ import annotations

from datetime import date
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from src.domain.entities import AcquirerTransaction
from src.infrastructure.persistence.repositories import TransactionRepository
from ..mappers import TransactionMapper
from ..models import TransactionModel

logger = structlog.get_logger(__name__)


class PostgreSQLTransactionRepository(TransactionRepository):
    """PostgreSQL implementation of TransactionRepository."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.mapper = TransactionMapper()
        self.logger = logger.bind(repository="PostgreSQLTransactionRepository")

    async def save(self, transaction: AcquirerTransaction) -> None:
        """Save a transaction."""
        try:
            stmt = select(TransactionModel).where(TransactionModel.id == UUID(transaction.id))
            result = await self.session.execute(stmt)
            existing = result.scalar_one_or_none()

            if existing:
                model = self.mapper.to_model(transaction, existing)
            else:
                model = self.mapper.to_model(transaction)
                self.session.add(model)

            await self.session.flush()

            self.logger.debug("transaction_saved", transaction_id=transaction.id)

        except Exception as exc:  # pragma: no cover - defensive logging
            self.logger.error("transaction_save_failed", transaction_id=transaction.id, error=str(exc))
            raise

    async def find_by_id(self, tenant_id: str, transaction_id: str) -> Optional[AcquirerTransaction]:
        """Find transaction by ID."""
        stmt = select(TransactionModel).where(
            TransactionModel.tenant_id == UUID(tenant_id),
            TransactionModel.id == UUID(transaction_id),
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()

        if model:
            return self.mapper.to_entity(model)
        return None

    async def find_by_date_range(
        self, tenant_id: str, start_date: date, end_date: date
    ) -> List[AcquirerTransaction]:
        """Find transactions in date range."""
        stmt = (
            select(TransactionModel)
            .where(
                TransactionModel.tenant_id == UUID(tenant_id),
                TransactionModel.transaction_date >= start_date,
                TransactionModel.transaction_date <= end_date,
            )
            .order_by(TransactionModel.transaction_date, TransactionModel.created_at)
        )

        result = await self.session.execute(stmt)
        models = result.scalars().all()

        transactions = [self.mapper.to_entity(model) for model in models]

        self.logger.debug(
            "transactions_found_by_date_range",
            tenant_id=tenant_id,
            count=len(transactions),
        )

        return transactions

    async def find_unmatched(self, tenant_id: str) -> List[AcquirerTransaction]:
        """Find unmatched transactions."""
        stmt = (
            select(TransactionModel)
            .where(
                TransactionModel.tenant_id == UUID(tenant_id),
                ~TransactionModel.matches.any(),
            )
            .order_by(TransactionModel.transaction_date.desc())
        )

        result = await self.session.execute(stmt)
        models = result.scalars().all()

        return [self.mapper.to_entity(model) for model in models]

    async def find_by_acquirer(
        self, tenant_id: str, acquirer: str, start_date: date, end_date: date
    ) -> List[AcquirerTransaction]:
        """Find transactions by acquirer and date range."""
        stmt = (
            select(TransactionModel)
            .where(
                TransactionModel.tenant_id == UUID(tenant_id),
                TransactionModel.acquirer == acquirer,
                TransactionModel.transaction_date >= start_date,
                TransactionModel.transaction_date <= end_date,
            )
            .order_by(TransactionModel.transaction_date)
        )

        result = await self.session.execute(stmt)
        models = result.scalars().all()

        return [self.mapper.to_entity(model) for model in models]
