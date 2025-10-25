"""Cash flow endpoints exposing forecast information."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import get_current_tenant_id, get_db_session
from src.application.use_cases.cash_flow import (
    GetCashFlowForecastRequest,
    GetCashFlowForecastUseCase,
)
from src.infrastructure.persistence.repositories import AcquirerTransactionRepository

router = APIRouter(prefix="/cash-flow", tags=["Cash Flow"])


@router.get("/forecast")
async def get_cash_flow_forecast(
    days_ahead: int = 30,
    tenant_id: str = Depends(get_current_tenant_id),
    db_session: AsyncSession = Depends(get_db_session),
):
    """Return forecasted cash flow for the authenticated tenant."""

    use_case = GetCashFlowForecastUseCase(
        acquirer_transaction_repo=AcquirerTransactionRepository(db_session)
    )

    result = await use_case.execute(
        GetCashFlowForecastRequest(tenant_id=tenant_id, days_ahead=days_ahead)
    )

    return {
        "summary_message": result.summary_message,
        "total_expected": float(result.total_expected),
        "total_received": float(result.total_received),
        "daily_forecast": result.daily_forecast,
    }
