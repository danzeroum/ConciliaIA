"""ML-based matching strategy providing heuristic scoring."""

from __future__ import annotations

from decimal import Decimal
from typing import List, Optional, Tuple
from uuid import uuid4

from src.domain.entities import AcquirerTransaction, MatchType, ReconciliationMatch, Sale
from .base_matcher import BaseMatcher


class MLMatcher(BaseMatcher):
    """Match sales and transactions using heuristic-based scoring."""

    def __init__(self, model_path: Optional[str] = None):
        super().__init__()
        self.model_path = model_path
        self.model = None  # Placeholder for future ML model loading

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
            best_score = Decimal("0.0")

            for transaction in remaining_transactions:
                score = self._calculate_ml_score(sale, transaction)
                if score >= Decimal("0.70") and score > best_score:
                    best_score = score
                    best_match = transaction

            if best_match:
                matches.append(
                    ReconciliationMatch(
                        id=f"match-{uuid4()}",
                        tenant_id=sale.tenant_id,
                        sale_id=sale.id,
                        transaction_id=best_match.id,
                        match_type=MatchType.ML_PREDICTED,
                        confidence=best_score,
                    )
                )
                remaining_transactions.remove(best_match)

                self.logger.debug(
                    "ml_match_found",
                    sale_id=sale.id,
                    transaction_id=best_match.id,
                    confidence=float(best_score),
                )
            else:
                unmatched_sales.append(sale)

        return matches, unmatched_sales, remaining_transactions

    def _calculate_ml_score(self, sale: Sale, transaction: AcquirerTransaction) -> Decimal:
        amount_diff = abs(sale.amount.amount - transaction.amount.amount)
        amount_similarity = max(
            Decimal("0.0"), Decimal("1.0") - (Decimal(str(amount_diff)) / sale.amount.amount)
        )

        date_diff_days = abs((sale.date - transaction.transaction_date).days)
        date_score = max(
            Decimal("0.0"), Decimal("1.0") - (Decimal(str(date_diff_days)) / Decimal("7"))
        )

        nsu_similarity = self._calculate_string_similarity(str(sale.nsu), str(transaction.nsu))

        auth_score = Decimal("0.0")
        if sale.authorization_code and transaction.authorization_code:
            auth_score = Decimal("1.0") if sale.authorization_code == transaction.authorization_code else Decimal("0.0")

        score = (
            amount_similarity * Decimal("0.40")
            + date_score * Decimal("0.30")
            + nsu_similarity * Decimal("0.20")
            + auth_score * Decimal("0.10")
        )

        return min(score, Decimal("0.94"))

    def _calculate_string_similarity(self, str1: str, str2: str) -> Decimal:
        if str1 == str2:
            return Decimal("1.0")

        set1 = set(str1.upper())
        set2 = set(str2.upper())
        if not set1 or not set2:
            return Decimal("0.0")

        intersection = len(set1 & set2)
        union = len(set1 | set2)
        if union == 0:
            return Decimal("0.0")

        return Decimal(str(intersection / union))
