"""Heuristic-based matching strategy (weighted scoring, no ML model yet)."""

from __future__ import annotations

from decimal import Decimal
from typing import List, Optional, Tuple
from uuid import uuid4

from rapidfuzz import fuzz

from src.domain.entities import AcquirerTransaction, MatchType, ReconciliationMatch, Sale
from .base_matcher import BaseMatcher


class MLMatcher(BaseMatcher):
    """Match sales and transactions using heuristic-based scoring.

    The name is kept for backwards compatibility; this is a weighted
    heuristic — not a trained model. See docs/ARCHITECTURE-POSTURE.md §IA.
    Weights: amount 40 %, date 30 %, NSU 20 %, auth_code 10 %.
    Score is capped at 0.94 so EXACT matches always rank higher (1.00).
    """

    def __init__(self, model_path: Optional[str] = None):
        super().__init__()
        self.model_path = model_path
        self.model = None  # reserved for future trained model

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
                        id=str(uuid4()),
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
            auth_score = (
                Decimal("1.0")
                if sale.authorization_code == transaction.authorization_code
                else Decimal("0.0")
            )

        score = (
            amount_similarity * Decimal("0.40")
            + date_score * Decimal("0.30")
            + nsu_similarity * Decimal("0.20")
            + auth_score * Decimal("0.10")
        )

        return min(score, Decimal("0.94"))

    @staticmethod
    def _calculate_string_similarity(str1: str, str2: str) -> Decimal:
        """Return normalised edit-distance similarity in [0, 1].

        Uses token_set_ratio from rapidfuzz so that reordered tokens
        (e.g. "123 ABC" vs "ABC 123") still score high, while
        numerically distinct strings like "1234" vs "4321" score
        correctly (≈0.57) instead of the old Jaccard 1.0 bug.
        """
        if str1 == str2:
            return Decimal("1.0")
        if not str1 or not str2:
            return Decimal("0.0")
        ratio = fuzz.token_set_ratio(str1.upper(), str2.upper())
        return Decimal(str(ratio / 100))
