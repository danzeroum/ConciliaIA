"""Abstract repository definitions for the domain layer."""

from __future__ import annotations

from datetime import date
from typing import List, Protocol

from src.domain.entities import (
    AcquirerTransaction,
    Divergence,
    ReconciliationMatch,
    Sale,
)


class SaleRepository(Protocol):
    """Repository responsible for sales persistence."""

    async def find_by_date_range(
        self, tenant_id: str, start_date: date, end_date: date
    ) -> List[Sale]: ...

    async def save(self, sale: Sale) -> None: ...


class TransactionRepository(Protocol):
    """Repository responsible for acquirer transactions."""

    async def find_by_date_range(
        self, tenant_id: str, start_date: date, end_date: date
    ) -> List[AcquirerTransaction]: ...


class MatchRepository(Protocol):
    """Repository responsible for reconciliation matches."""

    async def save(self, match: ReconciliationMatch) -> None: ...


class DivergenceRepository(Protocol):
    """Repository responsible for divergences."""

    async def save(self, divergence: Divergence) -> None: ...
