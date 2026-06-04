"""Fuzzy matching strategy implementing BR-002 and BR-003."""

from __future__ import annotations

from decimal import Decimal
from typing import List, Tuple
from uuid import uuid4

from src.domain.entities import AcquirerTransaction, MatchType, ReconciliationMatch, Sale
from .base_matcher import BaseMatcher


class FuzzyMatcher(BaseMatcher):
    """Match sales and transactions allowing tolerances in amount and date."""

    def __init__(self, amount_tolerance: Decimal = Decimal("0.50"), date_tolerance_days: int = 1):
        super().__init__()
        self.amount_tolerance = amount_tolerance
        self.date_tolerance_days = date_tolerance_days

    async def _match_logic(
        self,
        sales: List[Sale],
        transactions: List[AcquirerTransaction],
    ) -> Tuple[List[ReconciliationMatch], List[Sale], List[AcquirerTransaction]]:
        matches: List[ReconciliationMatch] = []
        remaining_transactions = transactions.copy()
        unmatched_sales: List[Sale] = []

        for sale in sales:
            best_match = None
            best_confidence = Decimal("0.0")

            for transaction in remaining_transactions:
                confidence = self._calculate_fuzzy_confidence(sale, transaction)
                if confidence >= Decimal("0.85") and confidence > best_confidence:
                    best_match = transaction
                    best_confidence = confidence

            if best_match:
                match_type = self._determine_match_type(sale, best_match)
                matches.append(
                    ReconciliationMatch(
                        id=str(uuid4()),
                        tenant_id=sale.tenant_id,
                        sale_id=sale.id,
                        transaction_id=best_match.id,
                        match_type=match_type,
                        confidence=best_confidence,
                    )
                )
                remaining_transactions.remove(best_match)

                self.logger.debug(
                    "fuzzy_match_found",
                    sale_id=sale.id,
                    transaction_id=best_match.id,
                    match_type=match_type.value,
                    confidence=float(best_confidence),
                )
            else:
                unmatched_sales.append(sale)

        return matches, unmatched_sales, remaining_transactions

    def _calculate_fuzzy_confidence(self, sale: Sale, transaction: AcquirerTransaction) -> Decimal:
        factors: dict[str, bool] = {}

        factors["nsu_match"] = sale.nsu == transaction.nsu

        amount_diff = abs(sale.amount.amount - transaction.amount.amount)
        factors["amount_match"] = amount_diff <= self.amount_tolerance

        date_diff_days = abs((sale.date - transaction.transaction_date).days)
        factors["date_match"] = date_diff_days <= self.date_tolerance_days

        if sale.authorization_code and transaction.authorization_code:
            factors["authorization_match"] = sale.authorization_code == transaction.authorization_code

        confidence = self._calculate_confidence(factors)

        if amount_diff > 0:
            penalty = (Decimal(str(amount_diff)) / self.amount_tolerance) * Decimal("0.10")
            confidence -= penalty

        return max(confidence, Decimal("0.0"))

    def _determine_match_type(self, sale: Sale, transaction: AcquirerTransaction) -> MatchType:
        amount_diff = abs(sale.amount.amount - transaction.amount.amount)
        date_diff = abs((sale.date - transaction.transaction_date).days)

        if amount_diff > 0 and date_diff == 0:
            return MatchType.FUZZY_AMOUNT
        if date_diff > 0 and amount_diff == 0:
            return MatchType.FUZZY_DATE
        return MatchType.FUZZY_AMOUNT
