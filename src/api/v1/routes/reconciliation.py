"""Reconciliation API routes."""

from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from src.api.dependencies import get_current_tenant, get_reconciliation_use_case
from src.application.use_cases.reconcile_transactions import ReconcileTransactionsUseCase
from src.domain.entities import Tenant

router = APIRouter()


class ReconciliationRequest(BaseModel):
    """Request model for reconciliation execution."""

    start_date: date = Field(..., description="Start date (YYYY-MM-DD)")
    end_date: date = Field(..., description="End date (YYYY-MM-DD)")
    auto_approve: bool = Field(
        default=True,
        description="Auto-approve matches with confidence >= 0.95",
    )


class ReconciliationResponse(BaseModel):
    """Response payload for reconciliation results."""

    matched: int = Field(..., description="Number of matches created")
    divergences: int = Field(..., description="Number of divergences detected")
    accuracy: float = Field(..., description="Accuracy percentage (0-100)")
    processing_time_ms: int = Field(..., description="Processing time in milliseconds")


@router.post(
    "/reconciliation/execute",
    response_model=ReconciliationResponse,
    status_code=status.HTTP_200_OK,
    summary="Execute reconciliation",
    description="Reconcilia vendas com transações de adquirentes para o período informado.",
)
async def execute_reconciliation(
    request: ReconciliationRequest,
    tenant: Tenant = Depends(get_current_tenant),
    use_case: ReconcileTransactionsUseCase = Depends(get_reconciliation_use_case),
) -> ReconciliationResponse:
    """Execute reconciliation for the authenticated tenant."""

    if request.start_date > request.end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="start_date must be <= end_date",
        )

    days_diff = (request.end_date - request.start_date).days
    if days_diff > 90:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Date range cannot exceed 90 days",
        )

    result = await use_case.execute(
        tenant_id=tenant.id,
        start_date=request.start_date,
        end_date=request.end_date,
    )

    return ReconciliationResponse(**result)
