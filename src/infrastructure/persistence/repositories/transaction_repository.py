"""Transaction repository."""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date
from typing import List, Optional

from src.domain.entities import AcquirerTransaction


class TransactionRepository(ABC):
    """Abstract repository for AcquirerTransactions."""

    @abstractmethod
    async def save(self, transaction: AcquirerTransaction) -> None:
        """Persist a transaction instance."""

    @abstractmethod
    async def find_by_id(
        self, tenant_id: str, transaction_id: str
    ) -> Optional[AcquirerTransaction]:
        """Retrieve a transaction by its identifier."""

    @abstractmethod
    async def find_by_date_range(
        self, tenant_id: str, start_date: date, end_date: date
    ) -> List[AcquirerTransaction]:
        """Return transactions that took place within the provided interval."""

    @abstractmethod
    async def find_unmatched(self, tenant_id: str) -> List[AcquirerTransaction]:
        """Return all transactions without an associated match."""

    @abstractmethod
    async def find_by_acquirer(
        self, tenant_id: str, acquirer: str, start_date: date, end_date: date
    ) -> List[AcquirerTransaction]:
        """Return transactions filtered by acquirer within a period."""
