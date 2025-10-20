"""Match repository."""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date
from typing import List, Optional

from src.domain.entities import ReconciliationMatch


class MatchRepository(ABC):
    """Abstract repository for ReconciliationMatches."""

    @abstractmethod
    async def save(self, match: ReconciliationMatch) -> None:
        """Persist a reconciliation match."""

    @abstractmethod
    async def find_by_id(
        self, tenant_id: str, match_id: str
    ) -> Optional[ReconciliationMatch]:
        """Retrieve a match by its identifier."""

    @abstractmethod
    async def find_by_sale(
        self, tenant_id: str, sale_id: str
    ) -> List[ReconciliationMatch]:
        """Return all matches associated with a sale."""

    @abstractmethod
    async def find_by_transaction(
        self, tenant_id: str, transaction_id: str
    ) -> List[ReconciliationMatch]:
        """Return all matches associated with a transaction."""

    @abstractmethod
    async def find_requiring_review(self, tenant_id: str) -> List[ReconciliationMatch]:
        """Return matches that still require manual review."""

    @abstractmethod
    async def find_by_date_range(
        self, tenant_id: str, start_date: date, end_date: date
    ) -> List[ReconciliationMatch]:
        """Return matches performed in the given date interval."""
