"""Simple in-memory repository implementations used for tests and bootstrapping."""

from __future__ import annotations

from datetime import date
from typing import Dict, List

from src.domain.entities import (
    AcquirerTransaction,
    Divergence,
    ReconciliationMatch,
    Sale,
)
from src.domain.repositories import (
    DivergenceRepository,
    MatchRepository,
    SaleRepository,
    TransactionRepository,
)


class InMemorySaleRepository(SaleRepository):
    """Store sales in memory for experiments and tests."""

    def __init__(self) -> None:
        self._sales: Dict[str, Sale] = {}

    async def find_by_date_range(
        self, tenant_id: str, start_date: date, end_date: date
    ) -> List[Sale]:
        return [
            sale
            for sale in self._sales.values()
            if sale.tenant_id == tenant_id and start_date <= sale.date <= end_date
        ]

    async def save(self, sale: Sale) -> None:
        self._sales[sale.id] = sale


class InMemoryTransactionRepository(TransactionRepository):
    """In-memory acquirer transaction repository."""

    def __init__(self) -> None:
        self._transactions: Dict[str, AcquirerTransaction] = {}

    async def find_by_date_range(
        self, tenant_id: str, start_date: date, end_date: date
    ) -> List[AcquirerTransaction]:
        return [
            txn
            for txn in self._transactions.values()
            if txn.tenant_id == tenant_id
            and start_date <= txn.transaction_date <= end_date
        ]

    async def save(self, transaction: AcquirerTransaction) -> None:
        self._transactions[transaction.id] = transaction


class InMemoryMatchRepository(MatchRepository):
    """Persist matches in memory for tests."""

    def __init__(self) -> None:
        self._matches: Dict[str, ReconciliationMatch] = {}

    async def save(self, match: ReconciliationMatch) -> None:
        self._matches[match.id] = match


class InMemoryDivergenceRepository(DivergenceRepository):
    """Store divergences for inspection."""

    def __init__(self) -> None:
        self._divergences: Dict[str, Divergence] = {}

    async def save(self, divergence: Divergence) -> None:
        self._divergences[divergence.id] = divergence
