"""Service responsible for flagging anomalies in reconciliation results."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import List
from uuid import uuid4

import structlog

from src.domain.entities import (
    AcquirerTransaction,
    Divergence,
    DivergenceType,
    ReconciliationMatch,
    Sale,
    Severity,
)
from src.domain.value_objects import Money

logger = structlog.get_logger(__name__)


class AnomalyDetectionService:
    """Detect anomalies such as missing transactions or unexpected fees."""

    async def detect_all_anomalies(
        self,
        tenant_id: str,
        unmatched_sales: List[Sale],
        unmatched_transactions: List[AcquirerTransaction],
        matches: List[ReconciliationMatch],
    ) -> List[Divergence]:
        divergences: List[Divergence] = []

        divergences.extend(await self._detect_missing_transactions(tenant_id, unmatched_sales))
        divergences.extend(
            await self._detect_duplicate_transactions(tenant_id, unmatched_transactions)
        )

        logger.info(
            "anomaly_detection_completed",
            tenant_id=tenant_id,
            total_divergences=len(divergences),
        )

        return divergences

    async def _detect_missing_transactions(
        self, tenant_id: str, unmatched_sales: List[Sale]
    ) -> List[Divergence]:
        divergences: List[Divergence] = []
        today = date.today()

        for sale in unmatched_sales:
            days_since_sale = (today - sale.date).days
            if days_since_sale < 7:
                continue

            if days_since_sale >= 90:
                severity = Severity.CRITICAL
                suggested_action = "Escalar com adquirente - risco de perda definitiva"
            elif days_since_sale >= 30:
                severity = Severity.HIGH
                suggested_action = "Acionar suporte da adquirente para status do pagamento"
            else:
                severity = Severity.MEDIUM
                suggested_action = "Validar captura com time financeiro"

            divergences.append(
                Divergence(
                    id=str(uuid4()),
                    tenant_id=tenant_id,
                    divergence_type=DivergenceType.MISSING_TRANSACTION,
                    severity=severity,
                    expected_value=sale.amount,
                    actual_value=Money(Decimal("0.00")),
                    suggested_action=suggested_action,
                )
            )

            logger.warning(
                "missing_transaction_detected",
                sale_id=sale.id,
                days_since_sale=days_since_sale,
                severity=severity.value,
            )

        return divergences

    async def _detect_duplicate_transactions(
        self, tenant_id: str, transactions: List[AcquirerTransaction]
    ) -> List[Divergence]:
        divergences: List[Divergence] = []
        seen: dict[tuple[str, Decimal, date], AcquirerTransaction] = {}

        for transaction in transactions:
            if transaction.has_installments:
                continue

            key = (str(transaction.nsu), transaction.amount.amount, transaction.transaction_date)
            if key in seen:
                divergences.append(
                    Divergence(
                        id=str(uuid4()),
                        tenant_id=tenant_id,
                        divergence_type=DivergenceType.DUPLICATE_TRANSACTION,
                        severity=Severity.HIGH,
                        expected_value=transaction.amount,
                        actual_value=transaction.amount * 2,
                        suggested_action=f"Contestar duplicidade com adquirente (NSU {transaction.nsu})",
                    )
                )

                logger.warning(
                    "duplicate_transaction_detected",
                    transaction_id=transaction.id,
                    original_id=seen[key].id,
                    nsu=str(transaction.nsu),
                )
            else:
                seen[key] = transaction

        return divergences

    def _calculate_severity_by_amount(self, amount: Money) -> Severity:
        if amount.amount >= Decimal("10000"):
            return Severity.CRITICAL
        if amount.amount >= Decimal("1000"):
            return Severity.HIGH
        if amount.amount >= Decimal("100"):
            return Severity.MEDIUM
        return Severity.LOW
