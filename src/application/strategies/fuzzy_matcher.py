"""Fuzzy matching strategy tolerant to small amount or date variations."""

from __future__ import annotations

from decimal import Decimal
from typing import List, Tuple

import structlog

from src.application.interfaces import MatchingStrategy
from src.domain.entities import (
    AcquirerTransaction,
    MatchType,
    ReconciliationMatch,
    Sale,
)

logger = structlog.get_logger(__name__)


class FuzzyMatcher(MatchingStrategy):
    """Match by accepting limited amount or date variance."""

    AMOUNT_TOLERANCE = Decimal("0.50")
    DATE_TOLERANCE_DAYS = 1

    async def match(
        self,
        sales: List[Sale],
        transactions: List[AcquirerTransaction],
    ) -> Tuple[List[ReconciliationMatch], List[Sale], List[AcquirerTransaction]]:
        logger.info(
            "fuzzy_matcher_started",
            sales=len(sales),
            transactions=len(transactions),
        )

        matches: List[ReconciliationMatch] = []
        unmatched_sales: List[Sale] = []
        matched_transaction_ids: set[str] = set()

        for sale in sales:
            best_candidate: AcquirerTransaction | None = None
            best_confidence = Decimal("0")

            for transaction in transactions:
                if transaction.id in matched_transaction_ids:
                    continue

                if sale.nsu != transaction.nsu:
                    continue

                amount_diff = abs(sale.amount.amount - transaction.gross_amount.amount)
                if amount_diff > self.AMOUNT_TOLERANCE:
                    continue

                date_diff_days = abs((sale.date - transaction.transaction_date).days)
                if date_diff_days > self.DATE_TOLERANCE_DAYS:
                    continue

                confidence = self._calculate_confidence(amount_diff, date_diff_days)
                if confidence > best_confidence:
                    best_confidence = confidence
                    best_candidate = transaction

            if best_candidate is None:
                unmatched_sales.append(sale)
                continue

            matches.append(
                self._create_match(
                    sale=sale,
                    transaction=best_candidate,
                    confidence=best_confidence,
                )
            )
            matched_transaction_ids.add(best_candidate.id)

        unmatched_transactions = [
            txn for txn in transactions if txn.id not in matched_transaction_ids
        ]

        logger.info(
            "fuzzy_matcher_completed",
            matches=len(matches),
            unmatched_sales=len(unmatched_sales),
        )

        return matches, unmatched_sales, unmatched_transactions

    def _calculate_confidence(
        self, amount_diff: Decimal, date_diff_days: int
    ) -> Decimal:
        if date_diff_days == 0:
            base = Decimal("0.95")
            penalty = (amount_diff / self.AMOUNT_TOLERANCE) * Decimal("0.10")
            confidence = base - penalty
            return max(confidence, Decimal("0.85"))

        if amount_diff == 0:
            return Decimal("0.90")
        return Decimal("0.85")

    def _create_match(
        self,
        sale: Sale,
        transaction: AcquirerTransaction,
        confidence: Decimal,
    ) -> ReconciliationMatch:
        amount_diff = abs(sale.amount.amount - transaction.gross_amount.amount)
        date_diff = abs((sale.date - transaction.transaction_date).days)

        if amount_diff > 0 and date_diff == 0:
            match_type = MatchType.FUZZY_AMOUNT
        elif date_diff > 0 and amount_diff == 0:
            match_type = MatchType.FUZZY_DATE
        else:
            match_type = MatchType.FUZZY_AMOUNT

        return ReconciliationMatch(
            id=_generate_uuid(),
            tenant_id=sale.tenant_id,
            sale_id=sale.id,
            transaction_id=transaction.id,
            match_type=match_type,
            confidence=confidence,
        )


def _generate_uuid() -> str:
    from uuid import uuid4

    return str(uuid4())


__all__ = ["FuzzyMatcher"]
