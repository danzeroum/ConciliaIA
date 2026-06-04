"""Installment matching strategy implementing BR-004."""

from __future__ import annotations

from decimal import Decimal
from typing import Dict, List, Tuple
from uuid import uuid4

from src.domain.entities import AcquirerTransaction, MatchType, ReconciliationMatch, Sale
from .base_matcher import BaseMatcher


class InstallmentMatcher(BaseMatcher):
    """Match sales to installment transactions."""

    async def _match_logic(
        self,
        sales: List[Sale],
        transactions: List[AcquirerTransaction],
    ) -> Tuple[List[ReconciliationMatch], List[Sale], List[AcquirerTransaction]]:
        matches: List[ReconciliationMatch] = []
        remaining_transactions = transactions.copy()
        unmatched_sales: List[Sale] = []

        groups = self._group_transactions_by_base_nsu(remaining_transactions)

        for sale in sales:
            if sale.installments <= 1:
                unmatched_sales.append(sale)
                continue

            base_nsu = self._extract_base_nsu(str(sale.nsu))
            group = groups.get(base_nsu)
            if not group:
                unmatched_sales.append(sale)
                continue

            if not self._validate_group(sale, group):
                unmatched_sales.append(sale)
                continue

            for transaction in group:
                matches.append(
                    ReconciliationMatch(
                        id=str(uuid4()),
                        tenant_id=sale.tenant_id,
                        sale_id=sale.id,
                        transaction_id=transaction.id,
                        match_type=MatchType.INSTALLMENT,
                        confidence=Decimal("0.98"),
                    )
                )
                remaining_transactions.remove(transaction)

            self.logger.debug(
                "installment_match_found",
                sale_id=sale.id,
                installments=len(group),
            )

        return matches, unmatched_sales, remaining_transactions

    def _group_transactions_by_base_nsu(
        self, transactions: List[AcquirerTransaction]
    ) -> Dict[str, List[AcquirerTransaction]]:
        groups: Dict[str, List[AcquirerTransaction]] = {}
        for transaction in transactions:
            if not transaction.has_installments:
                continue
            base_nsu = self._extract_base_nsu(str(transaction.nsu))
            groups.setdefault(base_nsu, []).append(transaction)
        return groups

    def _extract_base_nsu(self, nsu: str) -> str:
        for separator in ("-", "/", "_"):
            if separator in nsu:
                return nsu.split(separator)[0]
        return nsu

    def _validate_group(
        self, sale: Sale, transactions: List[AcquirerTransaction]
    ) -> bool:
        if len(transactions) != sale.installments:
            return False

        total_amount = sum(transaction.amount.amount for transaction in transactions)
        tolerance = Decimal("0.01") * sale.installments
        diff = abs(total_amount - sale.amount.amount)
        return diff <= tolerance
