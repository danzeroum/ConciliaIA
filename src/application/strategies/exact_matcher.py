"""Exact matching strategy that enforces strict equality rules."""

from __future__ import annotations

from decimal import Decimal
from typing import Dict, List, Tuple

import structlog

from src.application.interfaces import MatchingStrategy
from src.domain.entities import (
    AcquirerTransaction,
    MatchType,
    ReconciliationMatch,
    Sale,
)

logger = structlog.get_logger(__name__)


class ExactMatcher(MatchingStrategy):
    """Match sales and transactions using strict NSU, amount and date equality."""

    async def match(
        self,
        sales: List[Sale],
        transactions: List[AcquirerTransaction],
    ) -> Tuple[List[ReconciliationMatch], List[Sale], List[AcquirerTransaction]]:
        logger.info(
            "exact_matcher_started",
            sales=len(sales),
            transactions=len(transactions),
        )

        transaction_index = self._build_transaction_index(transactions)
        matched_transaction_ids: set[str] = set()
        matches: List[ReconciliationMatch] = []
        unmatched_sales: List[Sale] = []

        for sale in sales:
            key = self._build_key(
                sale.nsu,
                sale.amount.amount,
                sale.date.isoformat(),
            )
            candidates = transaction_index.get(key, [])
            transaction = self._pick_available_transaction(candidates, matched_transaction_ids)

            if transaction is None:
                unmatched_sales.append(sale)
                continue

            matches.append(self._create_match(sale, transaction))
            matched_transaction_ids.add(transaction.id)

        unmatched_transactions = [
            txn for txn in transactions if txn.id not in matched_transaction_ids
        ]

        logger.info(
            "exact_matcher_completed",
            matches=len(matches),
            unmatched_sales=len(unmatched_sales),
        )

        return matches, unmatched_sales, unmatched_transactions

    def _build_transaction_index(
        self, transactions: List[AcquirerTransaction]
    ) -> Dict[str, List[AcquirerTransaction]]:
        index: Dict[str, List[AcquirerTransaction]] = {}
        for transaction in transactions:
            key = self._build_key(
                transaction.nsu,
                transaction.gross_amount.amount,
                transaction.transaction_date.isoformat(),
            )
            index.setdefault(key, []).append(transaction)
        return index

    def _pick_available_transaction(
        self,
        candidates: List[AcquirerTransaction],
        matched_ids: set[str],
    ) -> AcquirerTransaction | None:
        for transaction in candidates:
            if transaction.id not in matched_ids:
                return transaction
        return None

    def _build_key(self, nsu: str, amount: Decimal, date_key: str) -> str:
        return f"{nsu}|{amount}|{date_key}"

    def _create_match(
        self, sale: Sale, transaction: AcquirerTransaction
    ) -> ReconciliationMatch:
        return ReconciliationMatch(
            id=_generate_uuid(),
            tenant_id=sale.tenant_id,
            sale_id=sale.id,
            transaction_id=transaction.id,
            match_type=MatchType.EXACT,
            confidence=Decimal("1.0"),
        )


def _generate_uuid() -> str:
    from uuid import uuid4

    return str(uuid4())


__all__ = ["ExactMatcher"]
