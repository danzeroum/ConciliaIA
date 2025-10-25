"""API routes for analytical reports."""

from __future__ import annotations

from datetime import date
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import get_current_tenant, get_db_session
from src.application.services.report_service import ReportService
from src.domain.entities import Tenant
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
from src.infrastructure.persistence.repositories.postgresql_settlement_repository import (
    PostgreSQLSettlementRepository,
)

router = APIRouter()


class AccuracyTrendPoint(BaseModel):
    date: str
    accuracy: float
    matches: int
    total_sales: int


class AccuracyReportResponse(BaseModel):
    period_start: str
    period_end: str
    overall_accuracy: float
    total_sales: int
    total_matches: int
    total_divergences: int
    trend: List[AccuracyTrendPoint]


class DivergenceByTypeItem(BaseModel):
    type: str
    count: int
    total_amount: float
    percentage: float


class DivergenceBySeverityItem(BaseModel):
    severity: str
    count: int
    total_amount: float


class DivergenceAnalysisResponse(BaseModel):
    period_start: str
    period_end: str
    total_divergences: int
    total_amount_at_risk: float
    by_type: List[DivergenceByTypeItem]
    by_severity: List[DivergenceBySeverityItem]
    resolution_rate: float
    avg_resolution_time_hours: float | None


class AcquirerPerformanceItem(BaseModel):
    acquirer: str
    total_transactions: int
    total_amount: float
    matched_count: int
    match_rate: float
    avg_mdr_rate: float | None
    total_mdr_amount: float


class AcquirerPerformanceResponse(BaseModel):
    period_start: str
    period_end: str
    acquirers: List[AcquirerPerformanceItem]


class SettlementBreakdownItem(BaseModel):
    date: str
    expected_amount: float
    received_count: int
    pending_count: int


class SettlementAnalysisResponse(BaseModel):
    period_start: str
    period_end: str
    total_expected: float
    total_received: float
    pending_settlement: float
    daily_breakdown: List[SettlementBreakdownItem]


class MDRVarianceItem(BaseModel):
    card_brand: str
    expected_mdr_rate: float
    actual_mdr_rate: float
    variance_percentage: float
    transaction_count: int
    variance_amount: float


class MDRVarianceResponse(BaseModel):
    period_start: str
    period_end: str
    total_variance_amount: float
    variances: List[MDRVarianceItem]


class CashflowTimelineItem(BaseModel):
    date: str
    expected_amount: float
    received_amount: float
    delayed_amount: float


class CashflowOverviewResponse(BaseModel):
    period_start: str
    period_end: str
    total_expected: float
    total_received: float
    delayed_amount: float
    pending_amount: float
    timeline: List[CashflowTimelineItem]


def get_report_service(
    db_session: AsyncSession = Depends(get_db_session),
) -> ReportService:
    sale_repo = PostgreSQLSaleRepository(db_session)
    transaction_repo = PostgreSQLTransactionRepository(db_session)
    match_repo = PostgreSQLMatchRepository(db_session)
    divergence_repo = PostgreSQLDivergenceRepository(db_session)
    settlement_repo = PostgreSQLSettlementRepository(db_session)
    return ReportService(
        sale_repo,
        transaction_repo,
        match_repo,
        divergence_repo,
        settlement_repo=settlement_repo,
    )


@router.get(
    "/reports/accuracy",
    response_model=AccuracyReportResponse,
    summary="Accuracy report",
    tags=["Reports"],
)
async def get_accuracy_report(
    tenant: Tenant = Depends(get_current_tenant),
    service: ReportService = Depends(get_report_service),
    start_date: date = Query(..., description="Report start date"),
    end_date: date = Query(..., description="Report end date"),
) -> AccuracyReportResponse:
    """Retrieve accuracy KPIs for the given period."""
    report = await service.generate_accuracy_report(tenant.id, start_date, end_date)
    return AccuracyReportResponse(
        period_start=start_date.isoformat(),
        period_end=end_date.isoformat(),
        overall_accuracy=report["overall_accuracy"],
        total_sales=report["total_sales"],
        total_matches=report["total_matches"],
        total_divergences=report["total_divergences"],
        trend=[AccuracyTrendPoint(**point) for point in report["trend"]],
    )


@router.get(
    "/reports/divergence-analysis",
    response_model=DivergenceAnalysisResponse,
    summary="Divergence analysis",
    tags=["Reports"],
)
async def get_divergence_analysis(
    tenant: Tenant = Depends(get_current_tenant),
    service: ReportService = Depends(get_report_service),
    start_date: date = Query(..., description="Report start date"),
    end_date: date = Query(..., description="Report end date"),
) -> DivergenceAnalysisResponse:
    """Analyze divergences for the provided period."""
    report = await service.generate_divergence_analysis(tenant.id, start_date, end_date)
    return DivergenceAnalysisResponse(
        period_start=start_date.isoformat(),
        period_end=end_date.isoformat(),
        total_divergences=report["total_divergences"],
        total_amount_at_risk=report["total_amount_at_risk"],
        by_type=[DivergenceByTypeItem(**item) for item in report["by_type"]],
        by_severity=[DivergenceBySeverityItem(**item) for item in report["by_severity"]],
        resolution_rate=report["resolution_rate"],
        avg_resolution_time_hours=report["avg_resolution_time_hours"],
    )


@router.get(
    "/reports/acquirer-performance",
    response_model=AcquirerPerformanceResponse,
    summary="Acquirer performance",
    tags=["Reports"],
)
async def get_acquirer_performance(
    tenant: Tenant = Depends(get_current_tenant),
    service: ReportService = Depends(get_report_service),
    start_date: date = Query(..., description="Report start date"),
    end_date: date = Query(..., description="Report end date"),
) -> AcquirerPerformanceResponse:
    """Compare acquirer performance across the period."""
    report = await service.generate_acquirer_performance(tenant.id, start_date, end_date)
    return AcquirerPerformanceResponse(
        period_start=start_date.isoformat(),
        period_end=end_date.isoformat(),
        acquirers=[AcquirerPerformanceItem(**item) for item in report["acquirers"]],
    )


@router.get(
    "/reports/settlement-analysis",
    response_model=SettlementAnalysisResponse,
    summary="Settlement analysis",
    tags=["Reports"],
)
async def get_settlement_analysis(
    tenant: Tenant = Depends(get_current_tenant),
    service: ReportService = Depends(get_report_service),
    start_date: date = Query(..., description="Report start date"),
    end_date: date = Query(..., description="Report end date"),
) -> SettlementAnalysisResponse:
    """Analyze settlement expectations and status."""
    report = await service.generate_settlement_analysis(tenant.id, start_date, end_date)
    return SettlementAnalysisResponse(
        period_start=start_date.isoformat(),
        period_end=end_date.isoformat(),
        total_expected=report["total_expected"],
        total_received=report["total_received"],
        pending_settlement=report["pending_settlement"],
        daily_breakdown=[
            SettlementBreakdownItem(**item) for item in report["daily_breakdown"]
        ],
    )


@router.get(
    "/reports/mdr-variance",
    response_model=MDRVarianceResponse,
    summary="MDR variance",
    tags=["Reports"],
)
async def get_mdr_variance(
    tenant: Tenant = Depends(get_current_tenant),
    service: ReportService = Depends(get_report_service),
    start_date: date = Query(..., description="Report start date"),
    end_date: date = Query(..., description="Report end date"),
) -> MDRVarianceResponse:
    """Retrieve MDR variance insights."""
    report = await service.generate_mdr_variance(tenant.id, start_date, end_date)
    return MDRVarianceResponse(
        period_start=start_date.isoformat(),
        period_end=end_date.isoformat(),
        total_variance_amount=report["total_variance_amount"],
        variances=[MDRVarianceItem(**item) for item in report["variances"]],
    )


@router.get(
    "/reports/cashflow-overview",
    response_model=CashflowOverviewResponse,
    summary="Cashflow forecast versus received",
    tags=["Reports"],
)
async def get_cashflow_overview(
    tenant: Tenant = Depends(get_current_tenant),
    service: ReportService = Depends(get_report_service),
    start_date: date = Query(..., description="Start date"),
    end_date: date = Query(..., description="End date"),
) -> CashflowOverviewResponse:
    if start_date > end_date:
        raise HTTPException(status_code=400, detail="Data inicial deve ser anterior à final")

    report = await service.generate_cashflow_overview(tenant.id, start_date, end_date)
    return CashflowOverviewResponse(
        period_start=report["period_start"],
        period_end=report["period_end"],
        total_expected=report["total_expected"],
        total_received=report["total_received"],
        delayed_amount=report["delayed_amount"],
        pending_amount=report["pending_amount"],
        timeline=[CashflowTimelineItem(**item) for item in report["timeline"]],
    )


__all__ = ["router"]
