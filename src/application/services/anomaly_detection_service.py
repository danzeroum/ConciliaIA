"""Service responsible for flagging anomalies in reconciliation results."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional

import structlog

from src.domain.entities import (
    AcquirerTransaction,
    Divergence,
    Money,
    Sale,
    Severity,
)

logger = structlog.get_logger(__name__)


class AnomalyDetectionService:
    """Detect anomalies such as missing transactions or unexpected fees."""

    MISSING_TX_THRESHOLDS_DAYS = (7, 30, 90)
    MDR_VARIANCE_THRESHOLDS = {
        "critical": (Decimal("0.20"), Decimal("1000")),
        "high": (Decimal("0.10"), Decimal("500")),
        "medium": (Decimal("0.05"), Decimal("100")),
    }

    async def detect_anomalies(
        self,
        tenant_id: str,
        unmatched_sales: List[Sale],
        unmatched_transactions: List[AcquirerTransaction],
    ) -> List[Divergence]:
        """Detect divergences for a tenant and return them."""

        divergences: List[Divergence] = []

        missing = self._detect_missing_transactions(tenant_id, unmatched_sales)
        divergences.extend(missing)

        unexpected = self._detect_unexpected_fees(tenant_id, unmatched_transactions)
        divergences.extend(unexpected)

        logger.info(
            "anomaly_detection_completed",
            tenant_id=tenant_id,
            total_divergences=len(divergences),
            missing_transactions=len(missing),
            unexpected_fees=len(unexpected),
        )

        return divergences

    def _detect_missing_transactions(
        self, tenant_id: str, unmatched_sales: List[Sale]
    ) -> List[Divergence]:
        divergences: List[Divergence] = []
        today = date.today()

        for sale in unmatched_sales:
            days_since_sale = (today - sale.date).days
            severity = self._calculate_missing_tx_severity(days_since_sale)
            if severity is None:
                continue

            divergences.append(
                self._create_missing_tx_divergence(
                    tenant_id=tenant_id,
                    sale=sale,
                    days_since_sale=days_since_sale,
                    severity=severity,
                )
            )

        return divergences

    def _calculate_missing_tx_severity(self, days_since_sale: int) -> Optional[Severity]:
        if days_since_sale >= self.MISSING_TX_THRESHOLDS_DAYS[2]:
            return Severity.CRITICAL
        if days_since_sale >= self.MISSING_TX_THRESHOLDS_DAYS[1]:
            return Severity.HIGH
        if days_since_sale >= self.MISSING_TX_THRESHOLDS_DAYS[0]:
            return Severity.MEDIUM
        return None

    def _create_missing_tx_divergence(
        self,
        tenant_id: str,
        sale: Sale,
        days_since_sale: int,
        severity: Severity,
    ) -> Divergence:
        return Divergence(
            id=_generate_uuid(),
            tenant_id=tenant_id,
            type="missing_transaction",
            sale_id=sale.id,
            transaction_id=None,
            severity=severity,
            amount_at_risk=sale.amount,
            detected_at=datetime.utcnow(),
        )

    def _detect_unexpected_fees(
        self, tenant_id: str, unmatched_transactions: List[AcquirerTransaction]
    ) -> List[Divergence]:
        divergences: List[Divergence] = []

        for transaction in unmatched_transactions:
            severity = self._calculate_fee_severity(transaction.mdr_fee)
            divergences.append(
                self._create_unexpected_fee_divergence(
                    tenant_id=tenant_id,
                    transaction=transaction,
                    severity=severity,
                )
            )

        return divergences

    def _calculate_fee_severity(self, fee_amount: Money) -> Severity:
        amount = fee_amount.amount
        if amount >= Decimal("1000"):
            return Severity.CRITICAL
        if amount >= Decimal("500"):
            return Severity.HIGH
        if amount >= Decimal("100"):
            return Severity.MEDIUM
        return Severity.LOW

    def _create_unexpected_fee_divergence(
        self,
        tenant_id: str,
        transaction: AcquirerTransaction,
        severity: Severity,
    ) -> Divergence:
        return Divergence(
            id=_generate_uuid(),
            tenant_id=tenant_id,
            type="unexpected_fee",
            sale_id=None,
            transaction_id=transaction.id,
            severity=severity,
            amount_at_risk=transaction.mdr_fee,
            detected_at=datetime.utcnow(),
        )


def _generate_uuid() -> str:
    from uuid import uuid4

    return str(uuid4())


__all__ = ["AnomalyDetectionService"]
