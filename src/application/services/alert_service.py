"""Service responsible for proactive alerts surfaced to the user."""

from __future__ import annotations

from datetime import date, timedelta
from typing import Dict, List

import structlog

from src.domain.entities import TransactionStatus
from src.infrastructure.persistence.repositories import (
    SettlementRepository,
    TransactionRepository,
)

logger = structlog.get_logger(__name__)


class AlertService:
    """Aggregate business signals that require the user's attention."""

    def __init__(
        self,
        settlement_repo: SettlementRepository,
        transaction_repo: TransactionRepository,
    ) -> None:
        self._settlement_repo = settlement_repo
        self._transaction_repo = transaction_repo
        self._logger = logger.bind(service="AlertService")

    async def generate_alerts(
        self, tenant_id: str, lookback_days: int = 30
    ) -> List[Dict[str, str]]:
        alerts: List[Dict[str, str]] = []

        delayed = await self._settlement_repo.find_delayed(tenant_id)
        for settlement in delayed:
            alerts.append(
                {
                    "type": "settlement_delay",
                    "severity": "high",
                    "title": "Pagamento atrasado",
                    "message": (
                        f"Recebimento de R$ {settlement.net_amount.amount:.2f} previsto para "
                        f"{settlement.expected_date.isoformat()} ainda não foi confirmado."
                    ),
                    "reference_id": settlement.id,
                }
            )

        end_date = date.today()
        start_date = end_date - timedelta(days=lookback_days)
        transactions = await self._transaction_repo.find_by_date_range(
            tenant_id, start_date, end_date
        )
        for txn in transactions:
            if txn.status == TransactionStatus.CHARGEBACK:
                alerts.append(
                    {
                        "type": "chargeback",
                        "severity": "critical",
                        "title": "Chargeback identificado",
                        "message": (
                            f"Contestação de R$ {txn.amount.amount:.2f} do dia "
                            f"{txn.transaction_date.isoformat()} - revise e conteste."
                        ),
                        "reference_id": txn.id,
                    }
                )

        self._logger.info(
            "alerts_generated", tenant_id=tenant_id, alerts=len(alerts)
        )

        return alerts


__all__ = ["AlertService"]
