"""Use case orchestrating the reconciliation workflow."""

from __future__ import annotations

from datetime import date, datetime
from typing import Dict

import structlog

from src.application.services import AnomalyDetectionService, MatchingService
from src.domain.entities import Severity
from src.domain.repositories import (
    DivergenceRepository,
    MatchRepository,
    SaleRepository,
    TransactionRepository,
)

logger = structlog.get_logger(__name__)


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
    ) -> Dict[str, int | float]:
        """Execute reconciliation for a date range and return aggregated metrics."""

        start_time = datetime.utcnow()
        logger.info(
            "reconciliation_started",
            tenant_id=tenant_id,
            start_date=str(start_date),
            end_date=str(end_date),
        )

        sales = await self.sale_repo.find_unmatched(
            tenant_id=tenant_id, start_date=start_date, end_date=end_date
        )
        transactions = await self.transaction_repo.find_unmatched(
            tenant_id=tenant_id, start_date=start_date, end_date=end_date
        )

        logger.info(
            "reconciliation_data_loaded",
            tenant_id=tenant_id,
            sales_count=len(sales),
            transactions_count=len(transactions),
        )

        matches, remaining_sales, remaining_transactions = await self.matching_service.match(
            sales=sales, transactions=transactions
        )

        for match in matches:
            await self.match_repo.save(match)
            if not match.requires_human_review():
                match.auto_approve()
                await self.match_repo.update(match)

        divergences = await self.anomaly_service.detect_anomalies(
            tenant_id=tenant_id,
            unmatched_sales=remaining_sales,
            unmatched_transactions=remaining_transactions,
        )

        for divergence in divergences:
            await self.divergence_repo.save(divergence)
            if divergence.severity == Severity.CRITICAL:
                logger.warning(
                    "critical_divergence_detected",
                    tenant_id=tenant_id,
                    divergence_id=divergence.id,
                    amount=float(divergence.amount_at_risk.amount),
                )

        total_sales = len(sales)
        matched_count = len(matches)
        accuracy = float(matched_count / total_sales * 100) if total_sales else 0.0
        processing_time_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)

        result: Dict[str, int | float] = {
            "matched": matched_count,
            "divergences": len(divergences),
            "accuracy": accuracy,
            "processing_time_ms": processing_time_ms,
        }

        logger.info("reconciliation_completed", tenant_id=tenant_id, **result)
        return result
