"""PostgreSQL implementation for storing bank transactions."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from src.domain.entities import BankTransaction
from src.domain.repositories import IBankTransactionRepository
from ..mappers import BankTransactionMapper
from ..models import BankTransactionModel

logger = structlog.get_logger(__name__)


class PostgreSQLBankTransactionRepository(IBankTransactionRepository):
    """Persist bank statement transactions using SQLAlchemy."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._mapper = BankTransactionMapper()
        self._logger = logger.bind(repository="PostgreSQLBankTransactionRepository")

    async def create(self, transaction: BankTransaction) -> BankTransaction:
        filters = [
            BankTransactionModel.tenant_id == UUID(transaction.tenant_id),
            BankTransactionModel.bank_account_id == transaction.bank_account_id,
        ]

        if transaction.bank_transaction_id:
            filters.append(
                BankTransactionModel.bank_transaction_id == transaction.bank_transaction_id
            )
        else:
            filters.extend(
                [
                    BankTransactionModel.transaction_date == transaction.transaction_date,
                    BankTransactionModel.amount == transaction.amount,
                ]
            )

        stmt = select(BankTransactionModel).where(and_(*filters))
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if model:
            model = self._mapper.to_model(transaction, model)
        else:
            model = self._mapper.to_model(transaction)
            self._session.add(model)

        await self._session.flush()

        entity = self._mapper.to_entity(model)
        self._logger.debug(
            "bank_transaction_saved",
            tenant_id=transaction.tenant_id,
            bank_account_id=transaction.bank_account_id,
            fitid=transaction.bank_transaction_id,
        )
        return entity


__all__ = ["PostgreSQLBankTransactionRepository"]
