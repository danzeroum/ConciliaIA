"""Exact matching strategy enforcing strict equality rules."""

from __future__ import annotations

from decimal import Decimal
from typing import List, Tuple
from uuid import uuid4

from src.domain.entities import AcquirerTransaction, MatchType, ReconciliationMatch, Sale
from .base_matcher import BaseMatcher


class ExactMatcher(BaseMatcher):
    """Match sales and transactions using strict NSU, amount and date equality."""

    async def _match_logic(
        self,
        sales: List[Sale],
        transactions: List[AcquirerTransaction],
    ) -> Tuple[List[ReconciliationMatch], List[Sale], List[AcquirerTransaction]]:
        matches: List[ReconciliationMatch] = []
        remaining_transactions = transactions.copy()
        unmatched_sales: List[Sale] = []

        for sale in sales:
            match = self._find_matching_transaction(sale, remaining_transactions)
            if not match:
                unmatched_sales.append(sale)
                continue

            matches.append(
                ReconciliationMatch(
                    id=str(uuid4()),
                    tenant_id=sale.tenant_id,
                    sale_id=sale.id,
                    transaction_id=match.id,
                    match_type=MatchType.EXACT,
                    confidence=Decimal("1.00"),
                )
            )
            remaining_transactions.remove(match)

            self.logger.debug(
                "exact_match_found",
                sale_id=sale.id,
                transaction_id=match.id,
                nsu=str(sale.nsu),
            )

        return matches, unmatched_sales, remaining_transactions

    def _find_matching_transaction(
        self, sale: Sale, transactions: List[AcquirerTransaction]
    ) -> AcquirerTransaction | None:
        for transaction in transactions:
            if (
                sale.nsu == transaction.nsu
                and sale.amount.amount == transaction.amount.amount
                and sale.date == transaction.transaction_date
            ):
                return transaction
        return None
