"""Proactive alert engine implementation."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal
from typing import Dict, List

import structlog

from src.domain.entities import AcquirerTransaction
from src.domain.repositories import IAcquirerTransactionRepository
from src.infrastructure.notification import NotificationService

logger = structlog.get_logger(__name__)


@dataclass(slots=True)
class AlertRule:
    """Definition of a proactive alert rule."""

    rule_id: str
    name: str
    description: str
    severity: str
    check_interval_hours: int = 24


class ProactiveAlertEngine:
    """Detect business anomalies and dispatch concise notifications."""

    RULES: List[AlertRule] = [
        AlertRule(
            rule_id="delayed_payment",
            name="Pagamento Atrasado",
            description="Detecta pagamentos pendentes há mais de 5 dias",
            severity="high",
        ),
        AlertRule(
            rule_id="sales_drop",
            name="Queda nas Vendas",
            description="Detecta queda > 30% comparado à média dos últimos 7 dias",
            severity="medium",
        ),
        AlertRule(
            rule_id="abnormal_mdr",
            name="Taxa MDR Anormal",
            description="Detecta taxa MDR > 2x o esperado",
            severity="high",
        ),
        AlertRule(
            rule_id="recurring_chargebacks",
            name="Chargebacks Recorrentes",
            description="Detecta mais de 3 chargebacks no mês",
            severity="critical",
        ),
    ]

    def __init__(
        self,
        acquirer_transaction_repo: IAcquirerTransactionRepository,
        notification_service: NotificationService,
    ) -> None:
        self._transactions = acquirer_transaction_repo
        self._notification_service = notification_service

    async def run_all_checks(self, tenant_id: str) -> List[Dict[str, object]]:
        """Execute all alert checks for a tenant and send notifications."""

        logger.info("alerts.run_all_checks.start", tenant_id=tenant_id)

        alerts_triggered: List[Dict[str, object]] = []

        delayed_alerts = await self._check_delayed_payments(tenant_id)
        alerts_triggered.extend(delayed_alerts)

        sales_drop_alerts = await self._check_sales_drop(tenant_id)
        alerts_triggered.extend(sales_drop_alerts)

        mdr_alerts = await self._check_abnormal_mdr(tenant_id)
        alerts_triggered.extend(mdr_alerts)

        chargeback_alerts = await self._check_recurring_chargebacks(tenant_id)
        alerts_triggered.extend(chargeback_alerts)

        for alert in alerts_triggered:
            await self._notification_service.send(
                tenant_id=tenant_id,
                title=alert["title"],
                message=alert["message"],
                priority=alert.get("severity", "info"),
                action_url=alert.get("action_url"),
            )

        logger.info(
            "alerts.run_all_checks.completed",
            tenant_id=tenant_id,
            total=len(alerts_triggered),
        )

        return alerts_triggered

    async def _check_delayed_payments(self, tenant_id: str) -> List[Dict[str, object]]:
        """Detect payments that should have been settled but remain pending."""

        cutoff_date = date.today() - timedelta(days=5)
        delayed_transactions = await self._transactions.find_delayed_settlements(
            tenant_id=tenant_id,
            cutoff_date=cutoff_date,
        )

        if not delayed_transactions:
            return []

        total_delayed = sum(
            self._money_amount(txn.net_amount or txn.amount)
            for txn in delayed_transactions
        )
        relevant_dates = [
            txn.settlement_date or txn.transaction_date
            for txn in delayed_transactions
            if (txn.settlement_date or txn.transaction_date) is not None
        ]

        if not relevant_dates:
            return []

        oldest_expected = min(relevant_dates)
        reference_date = oldest_expected.date() if hasattr(oldest_expected, "date") else oldest_expected
        days_late = max((date.today() - reference_date).days, 0)

        return [
            {
                "rule_id": "delayed_payment",
                "severity": "high",
                "title": "⚠️ Pagamentos Atrasados",
                "message": (
                    "Você tem "
                    f"{self._format_currency(total_delayed)} em pagamentos atrasados há "
                    f"{days_late} dias. Entre em contato com a adquirente."
                ),
                "action_url": "/transactions?filter=delayed",
                "data": {
                    "count": len(delayed_transactions),
                    "total_amount": float(total_delayed),
                    "days_late": days_late,
                },
            }
        ]

    async def _check_sales_drop(self, tenant_id: str) -> List[Dict[str, object]]:
        """Highlight significant drops in daily sales volume."""

        today = date.today()
        start_period = today - timedelta(days=7)

        transactions = await self._transactions.find_by_date_range(
            tenant_id=tenant_id,
            start_date=start_period,
            end_date=today,
        )

        if len(transactions) < 7:
            return []

        daily_totals: Dict[date, Decimal] = {}
        for txn in transactions:
            tx_date = txn.transaction_date
            if hasattr(tx_date, "date"):
                tx_date = tx_date.date()
            daily_totals.setdefault(tx_date, Decimal("0"))
            daily_totals[tx_date] += self._money_amount(txn.amount)

        past_days = [amount for day, amount in daily_totals.items() if day < today]
        if not past_days:
            return []

        avg_daily = sum(past_days) / Decimal(len(past_days))
        if avg_daily == 0:
            return []

        today_total = daily_totals.get(today, Decimal("0"))

        threshold = avg_daily * Decimal("0.70")
        if today_total >= threshold:
            return []

        drop_percentage = (avg_daily - today_total) / avg_daily * Decimal("100")

        return [
            {
                "rule_id": "sales_drop",
                "severity": "medium",
                "title": "📉 Queda nas Vendas",
                "message": (
                    "Suas vendas hoje estão "
                    f"{drop_percentage.quantize(Decimal('1'))}% abaixo da média. Tudo bem?"
                ),
                "action_url": "/dashboard",
                "data": {
                    "today_total": float(today_total),
                    "avg_daily": float(avg_daily),
                    "drop_percentage": float(drop_percentage),
                },
            }
        ]

    async def _check_abnormal_mdr(self, tenant_id: str) -> List[Dict[str, object]]:
        """Detect unusually high MDR fees within the last 30 days."""

        end_date = date.today()
        start_date = end_date - timedelta(days=30)

        transactions = await self._transactions.find_by_date_range(
            tenant_id=tenant_id,
            start_date=start_date,
            end_date=end_date,
        )

        if not transactions:
            return []

        total_gross = sum(self._money_amount(txn.amount) for txn in transactions)
        if total_gross == 0:
            return []

        total_fee = Decimal("0")
        for txn in transactions:
            if txn.mdr_amount:
                total_fee += self._money_amount(txn.mdr_amount)
            elif txn.mdr_rate:
                total_fee += self._money_amount(txn.amount) * txn.mdr_rate.value

        if total_fee == 0:
            return []

        avg_mdr_rate = total_fee / total_gross

        abnormal_transactions: List[AcquirerTransaction] = []
        for txn in transactions:
            if self._money_amount(txn.amount) <= Decimal("100"):
                continue
            actual_rate = None
            if txn.mdr_rate:
                actual_rate = txn.mdr_rate.value
            elif txn.mdr_amount and self._money_amount(txn.amount) > 0:
                actual_rate = self._money_amount(txn.mdr_amount) / self._money_amount(txn.amount)

            if actual_rate is None:
                continue

            if actual_rate > (avg_mdr_rate * Decimal("2")):
                abnormal_transactions.append(txn)

        if not abnormal_transactions:
            return []

        total_extra_charged = Decimal("0")
        for txn in abnormal_transactions:
            actual_fee = (
                self._money_amount(txn.mdr_amount)
                if txn.mdr_amount
                else self._money_amount(txn.amount) * (txn.mdr_rate.value if txn.mdr_rate else Decimal("0"))
            )
            expected_fee = self._money_amount(txn.amount) * avg_mdr_rate
            total_extra_charged += max(actual_fee - expected_fee, Decimal("0"))

        return [
            {
                "rule_id": "abnormal_mdr",
                "severity": "high",
                "title": "💰 Taxa MDR Anormal",
                "message": (
                    "Detectamos "
                    f"{len(abnormal_transactions)} transações com taxa acima do normal. "
                    "Você pode ter sido cobrado "
                    f"{self._format_currency(total_extra_charged)} a mais."
                ),
                "action_url": "/divergences?type=mdr",
                "data": {
                    "count": len(abnormal_transactions),
                    "extra_charged": float(total_extra_charged),
                    "avg_mdr": float(avg_mdr_rate * Decimal("100")),
                },
            }
        ]

    async def _check_recurring_chargebacks(self, tenant_id: str) -> List[Dict[str, object]]:
        """Flag tenants experiencing multiple chargebacks in the current month."""

        today = date.today()
        start_of_month = today.replace(day=1)

        chargebacks = await self._transactions.find_chargebacks(
            tenant_id=tenant_id,
            start_date=start_of_month,
            end_date=today,
        )

        if len(chargebacks) <= 3:
            return []

        total_loss = sum(
            abs(self._money_amount(txn.net_amount or txn.amount)) for txn in chargebacks
        )

        return [
            {
                "rule_id": "recurring_chargebacks",
                "severity": "critical",
                "title": "🚨 Chargebacks Recorrentes",
                "message": (
                    "Você teve "
                    f"{len(chargebacks)} chargebacks este mês "
                    f"({self._format_currency(total_loss)} de perda). Revise sua política de entrega/atendimento."
                ),
                "action_url": "/transactions?filter=chargeback",
                "data": {
                    "count": len(chargebacks),
                    "total_loss": float(total_loss),
                },
            }
        ]

    @staticmethod
    def _money_amount(money: "Money" | Decimal) -> Decimal:
        from src.domain.value_objects import Money  # local import to avoid cycles

        if isinstance(money, Money):
            return money.amount
        return Decimal(money)

    @staticmethod
    def _format_currency(value: Decimal) -> str:
        quantized = value.quantize(Decimal("0.01"))
        formatted = f"R$ {quantized:,.2f}"
        return formatted.replace(",", "X").replace(".", ",").replace("X", ".")


__all__ = ["AlertRule", "ProactiveAlertEngine"]
