"""Base class for matching strategies implementing shared behaviour."""

from __future__ import annotations

from abc import ABC, abstractmethod
from decimal import Decimal
from typing import List, Tuple

import structlog

from src.application.interfaces import MatchingStrategy
from src.domain.entities import AcquirerTransaction, ReconciliationMatch, Sale

logger = structlog.get_logger(__name__)


class BaseMatcher(MatchingStrategy, ABC):
    """Abstract base class implementing the Template Method pattern."""

    def __init__(self) -> None:
        self.logger = logger.bind(strategy=self.__class__.__name__)

    async def match(
        self,
        sales: List[Sale],
        transactions: List[AcquirerTransaction],
    ) -> Tuple[List[ReconciliationMatch], List[Sale], List[AcquirerTransaction]]:
        self.logger.info(
            "matching_started",
            sales_count=len(sales),
            transactions_count=len(transactions),
        )

        matches, unmatched_sales, unmatched_transactions = await self._match_logic(
            sales, transactions
        )

        self.logger.info(
            "matching_completed",
            matches_count=len(matches),
            unmatched_sales=len(unmatched_sales),
            unmatched_transactions=len(unmatched_transactions),
            match_rate=len(matches) / len(sales) if sales else 0,
        )

        return matches, unmatched_sales, unmatched_transactions

    @abstractmethod
    async def _match_logic(
        self,
        sales: List[Sale],
        transactions: List[AcquirerTransaction],
    ) -> Tuple[List[ReconciliationMatch], List[Sale], List[AcquirerTransaction]]:
        """Implement the strategy-specific matching logic."""

    def _calculate_confidence(self, factors: dict[str, bool]) -> Decimal:
        weights = {
            "nsu_match": Decimal("0.40"),
            "amount_match": Decimal("0.30"),
            "date_match": Decimal("0.20"),
            "authorization_match": Decimal("0.10"),
        }

        score = Decimal("0.0")
        for factor, weight in weights.items():
            if factors.get(factor, False):
                score += weight

        return min(score, Decimal("1.00"))
