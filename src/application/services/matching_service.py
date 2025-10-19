"""Matching service that orchestrates the cascade of strategies."""

from __future__ import annotations

from typing import List, Sequence, Tuple

import structlog

from src.application.interfaces import MatchingStrategy
from src.domain.entities import (
    AcquirerTransaction,
    ReconciliationMatch,
    Sale,
)

logger = structlog.get_logger(__name__)


class MatchingService:
    """Execute matching strategies in a cascade ordered by confidence."""

    def __init__(
        self,
        exact_matcher: MatchingStrategy,
        fuzzy_matcher: MatchingStrategy,
        ml_matcher: MatchingStrategy,
    ) -> None:
        self._strategies: Sequence[tuple[str, MatchingStrategy]] = (
            ("exact", exact_matcher),
            ("fuzzy", fuzzy_matcher),
            ("ml", ml_matcher),
        )

    async def match(
        self,
        sales: List[Sale],
        transactions: List[AcquirerTransaction],
    ) -> Tuple[List[ReconciliationMatch], List[Sale], List[AcquirerTransaction]]:
        """Run strategies sequentially returning matches and leftovers."""

        remaining_sales = list(sales)
        remaining_transactions = list(transactions)
        collected_matches: List[ReconciliationMatch] = []

        for name, strategy in self._strategies:
            if not remaining_sales or not remaining_transactions:
                break

            logger.info(
                "matching_strategy_started",
                strategy=name,
                remaining_sales=len(remaining_sales),
                remaining_transactions=len(remaining_transactions),
            )

            matches, remaining_sales, remaining_transactions = await strategy.match(
                sales=remaining_sales,
                transactions=remaining_transactions,
            )

            collected_matches.extend(matches)

            logger.info(
                "matching_strategy_completed",
                strategy=name,
                matches_found=len(matches),
                remaining_sales=len(remaining_sales),
            )

        return collected_matches, remaining_sales, remaining_transactions


__all__ = ["MatchingService"]
