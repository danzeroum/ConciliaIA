"""Machine learning powered matching strategy with heuristic fallback."""

from __future__ import annotations

from difflib import SequenceMatcher
from decimal import Decimal
from statistics import mean
from typing import List, Optional, Sequence, Tuple
import structlog

from src.application.interfaces import MatchingStrategy
from src.domain.entities import (
    AcquirerTransaction,
    MatchType,
    ReconciliationMatch,
    Sale,
)

logger = structlog.get_logger(__name__)


class MLMatcher(MatchingStrategy):
    """Use a probabilistic model for complex matches with heuristics fallback."""

    def __init__(self, model_path: Optional[str] = None) -> None:
        self._model = self._load_model(model_path) if model_path else None
        self._using_ml = self._model is not None

    async def match(
        self,
        sales: List[Sale],
        transactions: List[AcquirerTransaction],
    ) -> Tuple[List[ReconciliationMatch], List[Sale], List[AcquirerTransaction]]:
        if not sales or not transactions:
            return [], list(sales), list(transactions)

        if not self._using_ml:
            return await self._heuristic_match(sales, transactions)

        matches: List[ReconciliationMatch] = []
        unmatched_sales: List[Sale] = []
        matched_transaction_ids: set[str] = set()

        for sale in sales:
            best_candidate: AcquirerTransaction | None = None
            best_confidence = Decimal("0")

            for transaction in transactions:
                if transaction.id in matched_transaction_ids:
                    continue

                features = self._extract_features(sale, transaction)
                confidence = self._predict_confidence(features)

                if confidence > best_confidence:
                    best_confidence = confidence
                    best_candidate = transaction

            if best_candidate is None or best_confidence < Decimal("0.70"):
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

        return matches, unmatched_sales, unmatched_transactions

    async def _heuristic_match(
        self,
        sales: List[Sale],
        transactions: List[AcquirerTransaction],
    ) -> Tuple[List[ReconciliationMatch], List[Sale], List[AcquirerTransaction]]:
        matches: List[ReconciliationMatch] = []
        unmatched_sales: List[Sale] = []
        matched_transaction_ids: set[str] = set()

        for sale in sales:
            best_candidate: AcquirerTransaction | None = None
            best_score = 0.0

            for transaction in transactions:
                if transaction.id in matched_transaction_ids:
                    continue

                score = self._calculate_heuristic_score(sale, transaction)
                if score > best_score:
                    best_score = score
                    best_candidate = transaction

            if best_candidate is None or best_score < 0.70:
                unmatched_sales.append(sale)
                continue

            matches.append(
                self._create_match(
                    sale=sale,
                    transaction=best_candidate,
                    confidence=Decimal(str(round(min(best_score, 1.0), 2))),
                )
            )
            matched_transaction_ids.add(best_candidate.id)

        unmatched_transactions = [
            txn for txn in transactions if txn.id not in matched_transaction_ids
        ]

        return matches, unmatched_sales, unmatched_transactions

    def _calculate_heuristic_score(
        self, sale: Sale, transaction: AcquirerTransaction
    ) -> float:
        nsu_similarity = self._string_similarity(sale.nsu, transaction.nsu)

        gross_amount = float(transaction.gross_amount.amount)
        sale_amount = float(sale.amount.amount)
        amount_diff = abs(sale_amount - gross_amount)
        if gross_amount == 0:
            amount_similarity = 1.0 if sale_amount == 0 else 0.0
        else:
            amount_similarity = max(0.0, 1 - (amount_diff / gross_amount))

        date_diff_days = abs((sale.date - transaction.transaction_date).days)
        date_similarity = max(0.0, 1 - (date_diff_days / 7.0))

        return (
            0.4 * nsu_similarity
            + 0.4 * amount_similarity
            + 0.2 * date_similarity
        )

    def _string_similarity(self, left: str, right: str) -> float:
        if not left and not right:
            return 1.0
        return SequenceMatcher(None, left, right).ratio()

    def _extract_features(
        self, sale: Sale, transaction: AcquirerTransaction
    ) -> List[float]:
        nsu_similarity = self._string_similarity(sale.nsu, transaction.nsu)

        sale_amount = float(sale.amount.amount)
        gross_amount = float(transaction.gross_amount.amount)
        amount_diff_abs = abs(sale_amount - gross_amount)
        if gross_amount == 0:
            amount_diff_pct = 1.0 if amount_diff_abs else 0.0
        else:
            amount_diff_pct = amount_diff_abs / gross_amount

        date_diff_days = abs((sale.date - transaction.transaction_date).days)
        same_weekday = int(sale.date.weekday() == transaction.transaction_date.weekday())
        installments_match = int(sale.installments == transaction.installments)

        payment_is_credit = int("credit" in sale.payment_method.lower())

        return [
            float(nsu_similarity),
            float(amount_diff_abs),
            float(amount_diff_pct),
            float(date_diff_days),
            float(same_weekday),
            float(installments_match),
            float(payment_is_credit),
            float(date_diff_days**2),
        ]

    def _predict_confidence(self, features: Sequence[float]) -> Decimal:
        if self._model is None:
            numeric_features = list(features[:4])
            average = mean(numeric_features) if numeric_features else 0.0
            average = max(0.0, min(average, 1.0))
            return Decimal(str(round(average, 2)))

        try:
            proba = self._model.predict_proba([list(features)])[0][1]
            return Decimal(str(round(float(proba), 2)))
        except Exception as exc:  # pragma: no cover - safety fallback
            logger.error("ml_prediction_failed", error=str(exc))
            return Decimal("0.0")

    def _load_model(self, model_path: str):  # pragma: no cover - optional dependency
        try:
            import joblib

            model = joblib.load(model_path)
            return model
        except FileNotFoundError:
            logger.warning("ml_model_not_found", path=model_path)
        except ImportError as exc:
            logger.warning("ml_model_dependencies_missing", error=str(exc))
        except Exception as exc:
            logger.warning("ml_model_load_failed", path=model_path, error=str(exc))
        return None

    def _create_match(
        self,
        sale: Sale,
        transaction: AcquirerTransaction,
        confidence: Decimal,
    ) -> ReconciliationMatch:
        return ReconciliationMatch(
            id=_generate_uuid(),
            tenant_id=sale.tenant_id,
            sale_id=sale.id,
            transaction_id=transaction.id,
            match_type=MatchType.ML_PREDICTED,
            confidence=confidence,
        )


def _generate_uuid() -> str:
    from uuid import uuid4

    return str(uuid4())


__all__ = ["MLMatcher"]
