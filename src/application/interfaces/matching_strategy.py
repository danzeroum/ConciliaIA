"""Abstract contracts for reconciliation matching strategies."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Tuple

from src.domain.entities import (
    AcquirerTransaction,
    ReconciliationMatch,
    Sale,
)


class MatchingStrategy(ABC):
    """Defines the behaviour for a matching strategy implementation."""

    @abstractmethod
    async def match(
        self,
        sales: List[Sale],
        transactions: List[AcquirerTransaction],
    ) -> Tuple[List[ReconciliationMatch], List[Sale], List[AcquirerTransaction]]:
        """Match sales to transactions returning matches and the remaining items."""


__all__ = ["MatchingStrategy"]
