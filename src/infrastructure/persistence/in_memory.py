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
    """Keep track of sales in memory for quick experimentation."""

    def __init__(self) -> None:
        self._sales: Dict[str, Sale] = {}
        self._matched: set[str] = set()

    async def find_unmatched(
        self, tenant_id: str, start_date: date, end_date: date
    ) -> List[Sale]:
        return [
            sale
            for sale in self._sales.values()
            if sale.tenant_id == tenant_id
            and sale.id not in self._matched
            and start_date <= sale.date <= end_date
        ]

    async def save(self, sale: Sale) -> None:
        self._sales[sale.id] = sale

    async def mark_as_matched(self, sale_id: str) -> None:
        self._matched.add(sale_id)


class InMemoryTransactionRepository(TransactionRepository):
    """In-memory acquirer transaction repository."""

    def __init__(self) -> None:
        self._transactions: Dict[str, AcquirerTransaction] = {}
        self._matched: set[str] = set()

    async def find_unmatched(
        self, tenant_id: str, start_date: date, end_date: date
    ) -> List[AcquirerTransaction]:
        return [
            txn
            for txn in self._transactions.values()
            if txn.tenant_id == tenant_id
            and txn.id not in self._matched
            and start_date <= txn.transaction_date <= end_date
        ]

    async def save(self, transaction: AcquirerTransaction) -> None:
        self._transactions[transaction.id] = transaction

    async def mark_as_matched(self, transaction_id: str) -> None:
        self._matched.add(transaction_id)


class InMemoryMatchRepository(MatchRepository):
    """Persist matches in memory for tests."""

    def __init__(self) -> None:
        self._matches: Dict[str, ReconciliationMatch] = {}

    async def save(self, match: ReconciliationMatch) -> None:
        self._matches[match.id] = match

    async def update(self, match: ReconciliationMatch) -> None:
        self._matches[match.id] = match


class InMemoryDivergenceRepository(DivergenceRepository):
    """Store divergences for inspection."""

    def __init__(self) -> None:
        self._divergences: Dict[str, Divergence] = {}

    async def save(self, divergence: Divergence) -> None:
        self._divergences[divergence.id] = divergence


__all__ = [
    "InMemorySaleRepository",
    "InMemoryTransactionRepository",
    "InMemoryMatchRepository",
    "InMemoryDivergenceRepository",
]
