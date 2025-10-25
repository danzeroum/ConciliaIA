"""SQLAlchemy-backed repository for cash flow specific queries."""

from __future__ import annotations

from datetime import date
from typing import List
from uuid import UUID

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from src.domain.entities import AcquirerTransaction, TransactionStatus
from src.domain.repositories import IAcquirerTransactionRepository
from ..mappers import TransactionMapper
from ..models import TransactionModel

logger = structlog.get_logger(__name__)


class AcquirerTransactionRepository(IAcquirerTransactionRepository):
    """Repository specialised in settlement-oriented transaction lookups."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._mapper = TransactionMapper()
        self._logger = logger.bind(repository="AcquirerTransactionRepository")

    async def find_by_status_and_date_range(
        self,
        tenant_id: str,
        status: TransactionStatus,
        start_date: date,
        end_date: date,
    ) -> List[AcquirerTransaction]:
        status_value = status.value if hasattr(status, "value") else str(status)

        stmt: Select[TransactionModel] = (
            select(TransactionModel)
            .where(
                TransactionModel.tenant_id == UUID(tenant_id),
                TransactionModel.status == status_value,
                TransactionModel.settlement_date >= start_date,
                TransactionModel.settlement_date <= end_date,
            )
            .order_by(TransactionModel.settlement_date, TransactionModel.created_at)
        )

        result = await self._session.execute(stmt)
        models = result.scalars().all()

        entities = [self._mapper.to_entity(model) for model in models]

        self._logger.debug(
            "transactions_found_by_status", count=len(entities), status=status_value
        )

        return entities
