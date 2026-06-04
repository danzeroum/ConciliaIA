"""Divergence repository."""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date
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

    @abstractmethod
    async def find_critical_open(self, tenant_id: str) -> List[Divergence]:
        """Return critical divergences that remain open."""

    @abstractmethod
    async def find_by_date_range(
        self, tenant_id: str, start_date: date, end_date: date
    ) -> List[Divergence]:
        """Return divergences detected during the provided interval."""

    @abstractmethod
    async def find_paginated(
        self,
        tenant_id: str,
        *,
        status: Optional[DivergenceStatus] = None,
        divergence_type: Optional[str] = None,
        severity: Optional[Severity] = None,
        page: int = 1,
        page_size: int = 50,
    ) -> tuple[List[Divergence], int]:
        """Return a page of divergences and the total count for the filters."""
