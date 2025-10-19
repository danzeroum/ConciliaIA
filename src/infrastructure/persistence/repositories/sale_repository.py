"""Sale repository with PostgreSQL implementation."""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date
from typing import List, Optional

from src.domain.entities import Sale


class SaleRepository(ABC):
    """Abstract repository for Sales."""

    @abstractmethod
    async def save(self, sale: Sale) -> None:
        """Persist a sale instance."""

    @abstractmethod
    async def find_by_id(self, tenant_id: str, sale_id: str) -> Optional[Sale]:
        """Retrieve a sale by its identifier."""

    @abstractmethod
    async def find_by_date_range(
        self, tenant_id: str, start_date: date, end_date: date
    ) -> List[Sale]:
        """Return all sales that occurred within the provided interval."""

    @abstractmethod
    async def find_unmatched(self, tenant_id: str) -> List[Sale]:
        """Return all sales that have not yet been reconciled."""

    @abstractmethod
    async def find_by_nsu(self, tenant_id: str, nsu: str) -> List[Sale]:
        """Return sales matching the provided NSU pattern."""
