"""Service layer responsible for generating analytical reports."""

from __future__ import annotations

from collections import defaultdict
from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Any, Dict, Iterable, List

import structlog

from src.domain.entities import DivergenceStatus, Sale, TransactionStatus
from src.infrastructure.persistence.repositories import (
    DivergenceRepository,
    MatchRepository,
    SaleRepository,
    TransactionRepository,
)

logger = structlog.get_logger(__name__)


class ReportService:
    """Generate aggregated datasets used by analytical dashboards."""

    def __init__(
        self,
        sale_repo: SaleRepository,
        transaction_repo: TransactionRepository,
        match_repo: MatchRepository,
        divergence_repo: DivergenceRepository,
    ) -> None:
        self.sale_repo = sale_repo
        self.transaction_repo = transaction_repo
        self.match_repo = match_repo
        self.divergence_repo = divergence_repo

    async def generate_accuracy_report(
        self, tenant_id: str, start_date: date, end_date: date
    ) -> Dict[str, Any]:
        """Compute accuracy metrics for the provided interval."""
        sales = await self.sale_repo.find_by_date_range(tenant_id, start_date, end_date)
        matches = await self.match_repo.find_by_date_range(
            tenant_id, start_date, end_date
        )
        divergences = await self.divergence_repo.find_by_date_range(
            tenant_id, start_date, end_date
        )

        total_sales = len(sales)
        total_matches = len(matches)
        unresolved_divergences = [
            d for d in divergences if d.status != DivergenceStatus.RESOLVED
        ]
        total_divergences = len(unresolved_divergences)
        overall_accuracy = (
            (total_matches / total_sales) * 100 if total_sales > 0 else 0.0
        )

        trend: List[Dict[str, Any]] = []
        current = start_date
        sales_by_date = _group_sales_by_date(sales)
        matches_by_date = _group_matches_by_date(matches)

        while current <= end_date:
            day_sales = sales_by_date.get(current, [])
            day_matches = matches_by_date.get(current, [])
            daily_total = len(day_sales)
            daily_matched = len(day_matches)
            accuracy = (daily_matched / daily_total * 100) if daily_total else 0.0

            trend.append(
                {
                    "date": current.isoformat(),
                    "accuracy": round(accuracy, 2),
                    "matches": daily_matched,
                    "total_sales": daily_total,
                }
            )
            current += timedelta(days=1)

        logger.info(
            "accuracy_report_generated",
            tenant_id=tenant_id,
            total_sales=total_sales,
            total_matches=total_matches,
        )

        return {
            "overall_accuracy": round(overall_accuracy, 2),
            "total_sales": total_sales,
            "total_matches": total_matches,
            "total_divergences": total_divergences,
            "trend": trend,
        }

    async def generate_divergence_analysis(
        self, tenant_id: str, start_date: date, end_date: date
    ) -> Dict[str, Any]:
        """Aggregate divergences by type and severity."""
        divergences = await self.divergence_repo.find_by_date_range(
            tenant_id, start_date, end_date
        )

        total_divergences = len(divergences)
        total_amount_at_risk = sum(
            _divergence_amount(divergence) for divergence in divergences
        )

        by_type: Dict[str, Dict[str, float]] = defaultdict(lambda: {"count": 0, "amount": 0.0})
        for divergence in divergences:
            key = divergence.divergence_type.value
            by_type[key]["count"] += 1
            by_type[key]["amount"] += _divergence_amount(divergence)

        by_type_list = [
            {
                "type": type_name,
                "count": int(values["count"]),
                "total_amount": round(values["amount"], 2),
                "percentage": round(
                    (values["count"] / total_divergences * 100)
                    if total_divergences
                    else 0.0,
                    2,
                ),
            }
            for type_name, values in sorted(
                by_type.items(), key=lambda item: item[1]["count"], reverse=True
            )
        ]

        by_severity: Dict[str, Dict[str, float]] = defaultdict(
            lambda: {"count": 0, "amount": 0.0}
        )
        for divergence in divergences:
            key = divergence.severity.value
            by_severity[key]["count"] += 1
            by_severity[key]["amount"] += _divergence_amount(divergence)

        severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        by_severity_list = [
            {
                "severity": name,
                "count": int(values["count"]),
                "total_amount": round(values["amount"], 2),
            }
            for name, values in sorted(
                by_severity.items(),
                key=lambda item: severity_order.get(item[0], 99),
            )
        ]

        resolved = [div for div in divergences if div.status == DivergenceStatus.RESOLVED]
        resolution_rate = (
            len(resolved) / total_divergences * 100 if total_divergences else 0.0
        )

        resolution_times: List[float] = []
        for divergence in resolved:
            if divergence.detected_at and divergence.resolved_at:
                delta = divergence.resolved_at - divergence.detected_at
                resolution_times.append(delta.total_seconds() / 3600)
        avg_resolution = (
            sum(resolution_times) / len(resolution_times) if resolution_times else None
        )

        logger.info(
            "divergence_analysis_generated",
            tenant_id=tenant_id,
            total_divergences=total_divergences,
        )

        return {
            "total_divergences": total_divergences,
            "total_amount_at_risk": round(total_amount_at_risk, 2),
            "by_type": by_type_list,
            "by_severity": by_severity_list,
            "resolution_rate": round(resolution_rate, 2),
            "avg_resolution_time_hours": round(avg_resolution, 2) if avg_resolution else None,
        }

    async def generate_acquirer_performance(
        self, tenant_id: str, start_date: date, end_date: date
    ) -> Dict[str, Any]:
        """Compare acquirer metrics within the period."""
        transactions = await self.transaction_repo.find_by_date_range(
            tenant_id, start_date, end_date
        )
        matches = await self.match_repo.find_by_date_range(
            tenant_id, start_date, end_date
        )
        matched_transaction_ids = {match.transaction_id for match in matches}

        grouped: Dict[str, Dict[str, Any]] = defaultdict(
            lambda: {"transactions": [], "total_amount": 0.0, "matched": 0, "mdr_rates": [], "mdr_amount": 0.0}
        )

        for txn in transactions:
            acquirer_name = str(txn.acquirer)
            bucket = grouped[acquirer_name]
            bucket["transactions"].append(txn)
            bucket["total_amount"] += _money_to_float(txn.amount)
            if txn.id in matched_transaction_ids:
                bucket["matched"] += 1
            if txn.mdr_rate is not None:
                bucket["mdr_rates"].append(float(txn.mdr_rate.as_percentage()))
            if txn.mdr_amount is not None:
                bucket["mdr_amount"] += _money_to_float(txn.mdr_amount)

        acquirers = []
        for name, values in sorted(grouped.items()):
            total_txns = len(values["transactions"])
            matched = values["matched"]
            match_rate = (matched / total_txns * 100) if total_txns else 0.0
            avg_mdr = (
                sum(values["mdr_rates"]) / len(values["mdr_rates"])
                if values["mdr_rates"]
                else None
            )

            acquirers.append(
                {
                    "acquirer": name,
                    "total_transactions": total_txns,
                    "total_amount": round(values["total_amount"], 2),
                    "matched_count": matched,
                    "match_rate": round(match_rate, 2),
                    "avg_mdr_rate": round(avg_mdr, 2) if avg_mdr is not None else None,
                    "total_mdr_amount": round(values["mdr_amount"], 2),
                }
            )

        logger.info(
            "acquirer_performance_generated",
            tenant_id=tenant_id,
            acquirer_count=len(acquirers),
        )

        return {"acquirers": acquirers}

    async def generate_settlement_analysis(
        self, tenant_id: str, start_date: date, end_date: date
    ) -> Dict[str, Any]:
        """Provide insights into settlement expectations."""
        transactions = await self.transaction_repo.find_by_date_range(
            tenant_id, start_date, end_date
        )

        total_expected = sum(_money_to_float(txn.amount) for txn in transactions)

        received_transactions = [
            txn for txn in transactions if txn.status == TransactionStatus.APPROVED
        ]
        total_received = sum(
            _money_to_float(txn.amount) for txn in received_transactions
        )

        pending_transactions = [
            txn for txn in transactions if txn.status != TransactionStatus.APPROVED
        ]
        pending_total = sum(_money_to_float(txn.amount) for txn in pending_transactions)

        daily_breakdown: List[Dict[str, Any]] = []
        current = start_date
        transactions_by_date = defaultdict(list)
        for txn in transactions:
            transactions_by_date[txn.transaction_date].append(txn)

        while current <= end_date:
            day_transactions = transactions_by_date.get(current, [])
            expected = sum(_money_to_float(txn.amount) for txn in day_transactions)
            received_count = sum(
                1
                for txn in day_transactions
                if txn.status == TransactionStatus.APPROVED
            )
            pending_count = len(day_transactions) - received_count

            daily_breakdown.append(
                {
                    "date": current.isoformat(),
                    "expected_amount": round(expected, 2),
                    "received_count": received_count,
                    "pending_count": pending_count,
                }
            )
            current += timedelta(days=1)

        logger.info(
            "settlement_analysis_generated",
            tenant_id=tenant_id,
            total_expected=total_expected,
        )

        return {
            "total_expected": round(total_expected, 2),
            "total_received": round(total_received, 2),
            "pending_settlement": round(pending_total, 2),
            "daily_breakdown": daily_breakdown,
        }

    async def generate_mdr_variance(
        self, tenant_id: str, start_date: date, end_date: date
    ) -> Dict[str, Any]:
        """Calculate MDR variance per card brand."""
        transactions = await self.transaction_repo.find_by_date_range(
            tenant_id, start_date, end_date
        )

        expected_rates = {
            "visa": 2.5,
            "mastercard": 2.5,
            "elo": 2.8,
            "amex": 3.5,
            "hipercard": 2.9,
        }

        grouped: Dict[str, Dict[str, Any]] = defaultdict(
            lambda: {"rates": [], "amounts": []}
        )

        for txn in transactions:
            if txn.card_brand and txn.mdr_rate is not None:
                key = txn.card_brand.lower()
                grouped[key]["rates"].append(float(txn.mdr_rate.as_percentage()))
                grouped[key]["amounts"].append(_money_to_float(txn.amount))

        variances: List[Dict[str, Any]] = []
        total_variance_amount = Decimal("0")

        for brand, values in grouped.items():
            if not values["rates"]:
                continue
            actual = sum(values["rates"]) / len(values["rates"])
            expected = expected_rates.get(brand, 2.5)
            variance_percentage = actual - expected
            total_amount = sum(values["amounts"])
            variance_amount = Decimal(str(total_amount)) * Decimal(str(variance_percentage)) / Decimal("100")
            total_variance_amount += variance_amount

            variances.append(
                {
                    "card_brand": brand.title(),
                    "expected_mdr_rate": round(expected, 2),
                    "actual_mdr_rate": round(actual, 2),
                    "variance_percentage": round(variance_percentage, 2),
                    "transaction_count": len(values["rates"]),
                    "variance_amount": round(float(variance_amount), 2),
                }
            )

        variances.sort(key=lambda item: abs(item["variance_amount"]), reverse=True)

        logger.info(
            "mdr_variance_generated",
            tenant_id=tenant_id,
            total_variance=float(total_variance_amount),
        )

        return {
            "total_variance_amount": round(float(total_variance_amount), 2),
            "variances": variances,
        }


def _group_sales_by_date(sales: Iterable[Sale]) -> Dict[date, List[Sale]]:
    grouped: Dict[date, List[Sale]] = defaultdict(list)
    for sale in sales:
        grouped[sale.date].append(sale)
    return grouped


def _group_matches_by_date(matches: Iterable[Any]) -> Dict[date, List[Any]]:
    grouped: Dict[date, List[Any]] = defaultdict(list)
    for match in matches:
        matched_at = match.matched_at if isinstance(match.matched_at, datetime) else None
        if matched_at is not None:
            grouped[matched_at.date()].append(match)
    return grouped


def _divergence_amount(divergence: Any) -> float:
    amount = getattr(divergence, "difference", None)
    if amount is None or _money_to_float(amount) == 0.0:
        candidate = getattr(divergence, "actual_value", None) or getattr(
            divergence, "expected_value", None
        )
        return _money_to_float(candidate)
    return _money_to_float(amount)


def _money_to_float(money: Any | None) -> float:
    if money is None:
        return 0.0
    amount = getattr(money, "amount", None)
    if amount is None:
        return float(money)
    return float(amount)


__all__ = ["ReportService"]
