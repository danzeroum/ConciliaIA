"""Divergence repository."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Optional

from src.domain.entities import Divergence, DivergenceStatus, Severity


class DivergenceRepository(ABC):
    """Abstract repository for Divergences."""

    @abstractmethod
    async def save(self, divergence: Divergence) -> None:
        """Persist a divergence record."""

    @abstractmethod
    async def find_by_id(
        self, tenant_id: str, divergence_id: str
    ) -> Optional[Divergence]:
        """Retrieve a divergence by its identifier."""

    @abstractmethod
    async def find_by_status(
        self, tenant_id: str, status: DivergenceStatus
    ) -> List[Divergence]:
        """Return divergences filtered by their current status."""

    @abstractmethod
    async def find_by_severity(
        self, tenant_id: str, severity: Severity
    ) -> List[Divergence]:
        """Return divergences filtered by severity."""
