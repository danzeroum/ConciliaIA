"""Application service contracts used by use cases."""

from __future__ import annotations

from typing import List, Protocol, Tuple

from src.domain.entities import (
    AcquirerTransaction,
    Divergence,
    ReconciliationMatch,
    Sale,
)


class MatchingService(Protocol):
    """Contract for services responsible for matching sales and transactions."""

    async def match(
        self, sales: List[Sale], transactions: List[AcquirerTransaction]
    ) -> Tuple[List[ReconciliationMatch], List[Sale], List[AcquirerTransaction]]: ...


class AnomalyDetectionService(Protocol):
    """Contract for detecting divergences once matching is completed."""

    async def detect_anomalies(
        self,
        tenant_id: str,
        unmatched_sales: List[Sale],
        unmatched_transactions: List[AcquirerTransaction],
    ) -> List[Divergence]: ...


__all__ = ["MatchingService", "AnomalyDetectionService"]
