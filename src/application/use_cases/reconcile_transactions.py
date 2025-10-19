"""Use case orchestrating the reconciliation workflow."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import List

import structlog

from src.application.services import AnomalyDetectionService, MatchingService
from src.domain.entities import Divergence, ReconciliationMatch
from src.domain.repositories import (
    DivergenceRepository,
    MatchRepository,
    SaleRepository,
    TransactionRepository,
)

logger = structlog.get_logger(__name__)


@dataclass
class ReconciliationResult:
    """Aggregate result of the reconciliation process."""

    matches: List[ReconciliationMatch]
    divergences: List[Divergence]
    total_sales: int
    total_transactions: int
    matched_count: int
    unmatched_sales_count: int
    unmatched_transactions_count: int
    accuracy: Decimal
    precision: Decimal
    recall: Decimal


class ReconcileTransactionsUseCase:
    """Co-ordinates matching logic and persistence for a given tenant."""

    def __init__(
        self,
        sale_repo: SaleRepository,
        transaction_repo: TransactionRepository,
        match_repo: MatchRepository,
        divergence_repo: DivergenceRepository,
        matching_service: MatchingService,
        anomaly_service: AnomalyDetectionService,
    ) -> None:
        self.sale_repo = sale_repo
        self.transaction_repo = transaction_repo
        self.match_repo = match_repo
        self.divergence_repo = divergence_repo
        self.matching_service = matching_service
        self.anomaly_service = anomaly_service

    async def execute(
        self, tenant_id: str, start_date: date, end_date: date
    ) -> ReconciliationResult:
        logger.info(
            "reconciliation_started",
            tenant_id=tenant_id,
            start_date=str(start_date),
            end_date=str(end_date),
        )

        sales = await self.sale_repo.find_by_date_range(
            tenant_id=tenant_id, start_date=start_date, end_date=end_date
        )
        transactions = await self.transaction_repo.find_by_date_range(
            tenant_id=tenant_id, start_date=start_date, end_date=end_date
        )

        logger.info(
            "reconciliation_data_loaded",
            tenant_id=tenant_id,
            sales_count=len(sales),
            transactions_count=len(transactions),
        )

        matches, unmatched_sales, unmatched_transactions = await self.matching_service.match_all(
            sales=sales, transactions=transactions
        )

        divergences = await self.anomaly_service.detect_all_anomalies(
            tenant_id=tenant_id,
            unmatched_sales=unmatched_sales,
            unmatched_transactions=unmatched_transactions,
            matches=matches,
        )

        for match in matches:
            await self.match_repo.save(match)

        for divergence in divergences:
            await self.divergence_repo.save(divergence)

        result = self._calculate_metrics(
            sales,
            transactions,
            matches,
            unmatched_sales,
            unmatched_transactions,
            divergences,
        )

        logger.info(
            "reconciliation_completed",
            tenant_id=tenant_id,
            accuracy=float(result.accuracy),
            matches=result.matched_count,
            divergences=len(divergences),
        )

        return result

    def _calculate_metrics(
        self,
        sales: List,
        transactions: List,
        matches: List[ReconciliationMatch],
        unmatched_sales: List,
        unmatched_transactions: List,
        divergences: List[Divergence],
    ) -> ReconciliationResult:
        total_sales = len(sales)
        total_transactions = len(transactions)
        matched_count = len(matches)

        accuracy = (
            Decimal(str(matched_count / total_sales)) if total_sales > 0 else Decimal("0.0")
        )

        precision = Decimal("1.0") if matched_count > 0 else Decimal("0.0")

        recall_denominator = matched_count + len(unmatched_sales)
        recall = (
            Decimal(str(matched_count / recall_denominator))
            if recall_denominator > 0
            else Decimal("0.0")
        )

        return ReconciliationResult(
            matches=matches,
            divergences=divergences,
            total_sales=total_sales,
            total_transactions=total_transactions,
            matched_count=matched_count,
            unmatched_sales_count=len(unmatched_sales),
            unmatched_transactions_count=len(unmatched_transactions),
            accuracy=accuracy,
            precision=precision,
            recall=recall,
        )
