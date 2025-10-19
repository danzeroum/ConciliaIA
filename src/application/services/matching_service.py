"""Matching service orchestrating strategy cascade."""

from __future__ import annotations

from typing import List, Tuple

import structlog

from src.application.strategies import ExactMatcher, FuzzyMatcher, InstallmentMatcher, MLMatcher
from src.domain.entities import AcquirerTransaction, ReconciliationMatch, Sale

logger = structlog.get_logger(__name__)


class MatchingService:
    """Orchestrates multiple matching strategies in cascade."""

    def __init__(
        self,
        exact_matcher: ExactMatcher,
        fuzzy_matcher: FuzzyMatcher,
        ml_matcher: MLMatcher,
        installment_matcher: InstallmentMatcher | None = None,
    ) -> None:
        self.exact_matcher = exact_matcher
        self.fuzzy_matcher = fuzzy_matcher
        self.ml_matcher = ml_matcher
        self.installment_matcher = installment_matcher or InstallmentMatcher()
        self.logger = logger.bind(service="MatchingService")

    async def match_all(
        self,
        sales: List[Sale],
        transactions: List[AcquirerTransaction],
    ) -> Tuple[List[ReconciliationMatch], List[Sale], List[AcquirerTransaction]]:
        self.logger.info(
            "cascade_matching_started",
            sales_count=len(sales),
            transactions_count=len(transactions),
        )

        all_matches: List[ReconciliationMatch] = []
        remaining_sales = sales.copy()
        remaining_transactions = transactions.copy()

        if remaining_sales:
            matches, remaining_sales, remaining_transactions = await self.exact_matcher.match(
                remaining_sales, remaining_transactions
            )
            all_matches.extend(matches)
            self.logger.info("exact_matcher_completed", matches=len(matches))

        if remaining_sales:
            matches, remaining_sales, remaining_transactions = await self.installment_matcher.match(
                remaining_sales, remaining_transactions
            )
            all_matches.extend(matches)
            self.logger.info("installment_matcher_completed", matches=len(matches))

        if remaining_sales:
            matches, remaining_sales, remaining_transactions = await self.fuzzy_matcher.match(
                remaining_sales, remaining_transactions
            )
            all_matches.extend(matches)
            self.logger.info("fuzzy_matcher_completed", matches=len(matches))

        if remaining_sales:
            matches, remaining_sales, remaining_transactions = await self.ml_matcher.match(
                remaining_sales, remaining_transactions
            )
            all_matches.extend(matches)
            self.logger.info("ml_matcher_completed", matches=len(matches))

        match_rate = len(all_matches) / len(sales) if sales else 0.0

        self.logger.info(
            "cascade_matching_completed",
            total_matches=len(all_matches),
            unmatched_sales=len(remaining_sales),
            unmatched_transactions=len(remaining_transactions),
            match_rate=match_rate,
        )

        return all_matches, remaining_sales, remaining_transactions
