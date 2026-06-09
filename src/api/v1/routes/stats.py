"""API routes providing dashboard statistics."""

from __future__ import annotations

from collections import defaultdict
from datetime import date, timedelta
from typing import Dict, List

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import get_current_tenant, get_db_session
from src.domain.entities import DivergenceStatus, Tenant
from src.infrastructure.persistence.repositories.postgresql_divergence_repository import (
    PostgreSQLDivergenceRepository,
)
from src.infrastructure.persistence.repositories.postgresql_match_repository import (
    PostgreSQLMatchRepository,
)
from src.infrastructure.persistence.repositories.postgresql_sale_repository import (
    PostgreSQLSaleRepository,
)
from src.infrastructure.persistence.repositories.postgresql_transaction_repository import (
    PostgreSQLTransactionRepository,
)

router = APIRouter()


class KPIMetrics(BaseModel):
    accuracy: float = Field(..., description="Overall matching accuracy percentage")
    total_matches: int = Field(..., description="Total matches in period")
    pending_divergences: int = Field(..., description="Open divergences")
    resolved_today: int = Field(..., description="Divergences resolved today")
    total_sales: int = Field(..., description="Number of sales in period")
    total_transactions: int = Field(..., description="Number of transactions in period")
    total_amount_reconciled: float = Field(..., description="Total reconciled amount in BRL")


class TrendDataPoint(BaseModel):
    date: str
    value: float


class TopDivergenceType(BaseModel):
    type: str
    count: int


class AcquirerBreakdown(BaseModel):
    acquirer: str
    transactions: int
    amount: float


class DashboardStatsResponse(BaseModel):
    kpis: KPIMetrics
    accuracy_trend: List[TrendDataPoint]
    top_divergence_types: List[TopDivergenceType]
    acquirer_breakdown: List[AcquirerBreakdown]


async def _compute_dashboard_stats(
    db_session: AsyncSession, tenant_id: str, days: int
) -> Dict[str, object]:
    sale_repo = PostgreSQLSaleRepository(db_session)
    transaction_repo = PostgreSQLTransactionRepository(db_session)
    match_repo = PostgreSQLMatchRepository(db_session)
    divergence_repo = PostgreSQLDivergenceRepository(db_session)

    end_date = date.today()
    start_date = end_date - timedelta(days=days - 1)

    sales = await sale_repo.find_by_date_range(tenant_id, start_date, end_date)
    transactions = await transaction_repo.find_by_date_range(
        tenant_id, start_date, end_date
    )
    matches = await match_repo.find_by_date_range(tenant_id, start_date, end_date)
    divergences = await divergence_repo.find_by_date_range(
        tenant_id, start_date, end_date
    )

    total_sales = len(sales)
    total_transactions = len(transactions)
    total_matches = len(matches)

    accuracy = (total_matches / total_sales * 100) if total_sales else 0.0

    pending_divergences = sum(
        1 for divergence in divergences if divergence.status != DivergenceStatus.RESOLVED
    )

    today = date.today()
    resolved_today = sum(
        1
        for divergence in divergences
        if divergence.resolved_at and divergence.resolved_at.date() == today
    )

    sale_map = {sale.id: sale for sale in sales}
    total_amount_reconciled = sum(
        float(sale_map[match.sale_id].amount.amount)
        for match in matches
        if match.sale_id in sale_map
    )

    trend_days = min(days, 30)
    accuracy_trend: List[TrendDataPoint] = []
    sales_by_date = defaultdict(list)
    for sale in sales:
        sales_by_date[sale.date].append(sale)
    matches_by_date = defaultdict(list)
    for match in matches:
        if match.matched_at:
            matches_by_date[match.matched_at.date()].append(match)

    for offset in range(trend_days):
        day = end_date - timedelta(days=trend_days - 1 - offset)
        day_sales = sales_by_date.get(day, [])
        day_matches = matches_by_date.get(day, [])
        value = (len(day_matches) / len(day_sales) * 100) if day_sales else 0.0
        accuracy_trend.append(TrendDataPoint(date=day.isoformat(), value=round(value, 2)))

    divergence_counter: Dict[str, int] = defaultdict(int)
    for divergence in divergences:
        if divergence.status != DivergenceStatus.RESOLVED:
            divergence_counter[divergence.divergence_type.value] += 1

    top_divergence_types = [
        {"type": dtype, "count": count}
        for dtype, count in sorted(
            divergence_counter.items(), key=lambda item: item[1], reverse=True
        )[:5]
    ]

    acquirer_aggregation: Dict[str, Dict[str, float | int]] = defaultdict(
        lambda: {"transactions": 0, "amount": 0.0}
    )
    for txn in transactions:
        key = str(txn.acquirer)
        acquirer_aggregation[key]["transactions"] = acquirer_aggregation[key][
            "transactions"
        ] + 1
        acquirer_aggregation[key]["amount"] = acquirer_aggregation[key]["amount"] + float(
            txn.amount.amount
        )

    acquirer_breakdown = [
        {
            "acquirer": acquirer,
            "transactions": data["transactions"],
            "amount": round(data["amount"], 2),
        }
        for acquirer, data in sorted(
            acquirer_aggregation.items(), key=lambda item: item[1]["amount"], reverse=True
        )
    ]

    kpis = KPIMetrics(
        accuracy=round(accuracy, 2),
        total_matches=total_matches,
        pending_divergences=pending_divergences,
        resolved_today=resolved_today,
        total_sales=total_sales,
        total_transactions=total_transactions,
        total_amount_reconciled=round(total_amount_reconciled, 2),
    )

    return {
        "kpis": kpis,
        "accuracy_trend": accuracy_trend,
        "top_divergence_types": top_divergence_types,
        "acquirer_breakdown": acquirer_breakdown,
    }


@router.get(
    "/stats/dashboard",
    response_model=DashboardStatsResponse,
    summary="Dashboard statistics",
    tags=["Statistics"],
)
async def get_dashboard_stats(
    tenant: Tenant = Depends(get_current_tenant),
    db_session: AsyncSession = Depends(get_db_session),
    days: int = Query(30, ge=1, le=90, description="Number of days to consider"),
) -> DashboardStatsResponse:
    """Return dashboard metrics and charts."""
    stats = await _compute_dashboard_stats(db_session, tenant.id, days)
    return DashboardStatsResponse(**stats)


@router.get(
    "/stats/kpis",
    response_model=KPIMetrics,
    summary="Dashboard KPIs",
    tags=["Statistics"],
)
async def get_kpis(
    tenant: Tenant = Depends(get_current_tenant),
    db_session: AsyncSession = Depends(get_db_session),
    days: int = Query(30, ge=1, le=90, description="Number of days to consider"),
) -> KPIMetrics:
    """Return only the KPI metrics."""
    stats = await _compute_dashboard_stats(db_session, tenant.id, days)
    return stats["kpis"]


__all__ = ["router"]
