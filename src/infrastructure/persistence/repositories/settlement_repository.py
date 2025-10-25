"""Settlement repository abstraction."""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date
from typing import List, Optional

from src.domain.entities import Settlement, SettlementStatus


class SettlementRepository(ABC):
    """Abstract repository for Settlements."""

    @abstractmethod
    async def save(self, settlement: Settlement) -> None:
        """Persist a settlement instance."""

    @abstractmethod
    async def find_by_id(self, tenant_id: str, settlement_id: str) -> Optional[Settlement]:
        """Retrieve a settlement by its identifier."""

    @abstractmethod
    async def find_by_status(self, tenant_id: str, status: SettlementStatus) -> List[Settlement]:
        """Return settlements filtered by status."""

    @abstractmethod
    async def find_delayed(self, tenant_id: str, reference_date: date | None = None) -> List[Settlement]:
        """Return settlements considered delayed relative to the reference date."""

    @abstractmethod
    async def find_by_period(
        self, tenant_id: str, start_date: date, end_date: date
    ) -> List[Settlement]:
        """Return settlements expected within the provided window."""
