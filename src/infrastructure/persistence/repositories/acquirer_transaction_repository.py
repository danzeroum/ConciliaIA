"""SQLAlchemy-backed repository for cash flow specific queries."""

from __future__ import annotations

from datetime import date, datetime
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

    async def find_by_date_range(
        self, tenant_id: str, start_date: date, end_date: date
    ) -> List[AcquirerTransaction]:
        stmt: Select[TransactionModel] = (
            select(TransactionModel)
            .where(
                TransactionModel.tenant_id == UUID(tenant_id),
                TransactionModel.transaction_date >= start_date,
                TransactionModel.transaction_date <= end_date,
            )
            .order_by(TransactionModel.transaction_date, TransactionModel.created_at)
        )

        result = await self._session.execute(stmt)
        models = result.scalars().all()
        entities = [self._mapper.to_entity(model) for model in models]

        self._logger.debug(
            "transactions_found_by_date_range",
            count=len(entities),
            start=str(start_date),
            end=str(end_date),
        )

        return entities

    async def find_delayed_settlements(
        self,
        tenant_id: str,
        cutoff_date: date,
    ) -> List[AcquirerTransaction]:
        pending_statuses = [
            TransactionStatus.PENDING.value,
            TransactionStatus.APPROVED.value,
        ]

        stmt: Select[TransactionModel] = (
            select(TransactionModel)
            .where(
                TransactionModel.tenant_id == UUID(tenant_id),
                TransactionModel.settlement_date.isnot(None),
                TransactionModel.settlement_date <= cutoff_date,
                TransactionModel.status.in_(pending_statuses),
            )
            .order_by(TransactionModel.settlement_date.asc())
        )

        result = await self._session.execute(stmt)
        models = result.scalars().all()
        entities = [self._mapper.to_entity(model) for model in models]

        self._logger.debug(
            "transactions_delayed_settlements",
            count=len(entities),
            cutoff=str(cutoff_date),
        )

        return entities

    async def find_chargebacks(
        self,
        tenant_id: str,
        start_date: date,
        end_date: date,
    ) -> List[AcquirerTransaction]:
        start_dt = datetime.combine(start_date, datetime.min.time())
        end_dt = datetime.combine(end_date, datetime.max.time())

        stmt: Select[TransactionModel] = (
            select(TransactionModel)
            .where(
                TransactionModel.tenant_id == UUID(tenant_id),
                TransactionModel.transaction_date >= start_dt,
                TransactionModel.transaction_date <= end_dt,
                TransactionModel.status == TransactionStatus.CHARGEBACK.value,
            )
            .order_by(TransactionModel.transaction_date.asc())
        )

        result = await self._session.execute(stmt)
        models = result.scalars().all()
        entities = [self._mapper.to_entity(model) for model in models]

        self._logger.debug(
            "transactions_chargebacks",
            count=len(entities),
            start=str(start_date),
            end=str(end_date),
        )

        return entities
