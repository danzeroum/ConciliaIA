"""Simple in-memory repository implementations used for tests and bootstrapping."""

from __future__ import annotations

from datetime import date
from typing import Dict, List, Optional, Set

from src.domain.entities import (
    AcquirerTransaction,
    Divergence,
    DivergenceStatus,
    ReconciliationMatch,
    Sale,
    Severity,
)
from src.infrastructure.persistence.repositories import (
    DivergenceRepository,
    MatchRepository,
    SaleRepository,
    TransactionRepository,
)


class InMemorySaleRepository(SaleRepository):
    """Store sales in memory for experiments and tests."""

    def __init__(self) -> None:
        self._sales: Dict[str, Sale] = {}
        self._matched_sales: Set[str] = set()

    async def find_by_id(self, tenant_id: str, sale_id: str) -> Optional[Sale]:
        sale = self._sales.get(sale_id)
        if sale and sale.tenant_id == tenant_id:
            return sale
        return None

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

    async def find_unmatched(self, tenant_id: str) -> List[Sale]:
        return [
            sale
            for sale in self._sales.values()
            if sale.tenant_id == tenant_id and sale.id not in self._matched_sales
        ]

    async def find_by_nsu(self, tenant_id: str, nsu: str) -> List[Sale]:
        return [
            sale
            for sale in self._sales.values()
            if sale.tenant_id == tenant_id and nsu.lower() in str(sale.nsu).lower()
        ]

    def mark_as_matched(self, sale_id: str) -> None:
        self._matched_sales.add(sale_id)


class InMemoryTransactionRepository(TransactionRepository):
    """In-memory acquirer transaction repository."""

    def __init__(self) -> None:
        self._transactions: Dict[str, AcquirerTransaction] = {}
        self._matched_transactions: Set[str] = set()

    async def find_by_id(
        self, tenant_id: str, transaction_id: str
    ) -> Optional[AcquirerTransaction]:
        transaction = self._transactions.get(transaction_id)
        if transaction and transaction.tenant_id == tenant_id:
            return transaction
        return None

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

    async def find_unmatched(self, tenant_id: str) -> List[AcquirerTransaction]:
        return [
            txn
            for txn in self._transactions.values()
            if txn.tenant_id == tenant_id and txn.id not in self._matched_transactions
        ]

    async def find_by_acquirer(
        self, tenant_id: str, acquirer: str, start_date: date, end_date: date
    ) -> List[AcquirerTransaction]:
        return [
            txn
            for txn in self._transactions.values()
            if txn.tenant_id == tenant_id
            and str(txn.acquirer).lower() == acquirer.lower()
            and start_date <= txn.transaction_date <= end_date
        ]

    def mark_as_matched(self, transaction_id: str) -> None:
        self._matched_transactions.add(transaction_id)


class InMemoryMatchRepository(MatchRepository):
    """Persist matches in memory for tests."""

    def __init__(
        self,
        sale_repo: InMemorySaleRepository | None = None,
        transaction_repo: InMemoryTransactionRepository | None = None,
    ) -> None:
        self._matches: Dict[str, ReconciliationMatch] = {}
        self._sale_repo = sale_repo
        self._transaction_repo = transaction_repo

    async def save(self, match: ReconciliationMatch) -> None:
        self._matches[match.id] = match
        if self._sale_repo is not None:
            self._sale_repo.mark_as_matched(match.sale_id)
        if self._transaction_repo is not None:
            self._transaction_repo.mark_as_matched(match.transaction_id)

    async def find_by_id(
        self, tenant_id: str, match_id: str
    ) -> Optional[ReconciliationMatch]:
        match = self._matches.get(match_id)
        if match and match.tenant_id == tenant_id:
            return match
        return None

    async def find_by_sale(
        self, tenant_id: str, sale_id: str
    ) -> List[ReconciliationMatch]:
        return [
            match
            for match in self._matches.values()
            if match.tenant_id == tenant_id and match.sale_id == sale_id
        ]

    async def find_by_transaction(
        self, tenant_id: str, transaction_id: str
    ) -> List[ReconciliationMatch]:
        return [
            match
            for match in self._matches.values()
            if match.tenant_id == tenant_id and match.transaction_id == transaction_id
        ]

    async def find_requiring_review(self, tenant_id: str) -> List[ReconciliationMatch]:
        return [
            match
            for match in self._matches.values()
            if match.tenant_id == tenant_id and match.requires_review
        ]


class InMemoryDivergenceRepository(DivergenceRepository):
    """Store divergences for inspection."""

    def __init__(self) -> None:
        self._divergences: Dict[str, Divergence] = {}

    async def save(self, divergence: Divergence) -> None:
        self._divergences[divergence.id] = divergence

    async def find_by_id(
        self, tenant_id: str, divergence_id: str
    ) -> Optional[Divergence]:
        divergence = self._divergences.get(divergence_id)
        if divergence and divergence.tenant_id == tenant_id:
            return divergence
        return None

    async def find_by_status(
        self, tenant_id: str, status: DivergenceStatus
    ) -> List[Divergence]:
        return [
            divergence
            for divergence in self._divergences.values()
            if divergence.tenant_id == tenant_id and divergence.status == status
        ]

    async def find_by_severity(
        self, tenant_id: str, severity: Severity
    ) -> List[Divergence]:
        return [
            divergence
            for divergence in self._divergences.values()
            if divergence.tenant_id == tenant_id and divergence.severity == severity
        ]

    async def find_critical_open(self, tenant_id: str) -> List[Divergence]:
        return [
            divergence
            for divergence in self._divergences.values()
            if divergence.tenant_id == tenant_id
            and divergence.severity == Severity.CRITICAL
            and divergence.status == DivergenceStatus.OPEN
        ]
