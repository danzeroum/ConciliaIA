"""Endpoints for automatic bank reconciliation."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import List

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import get_current_tenant, get_db_session
from src.application.use_cases.auto_bank_reconciliation import (
    AutoBankReconciliationRequest,
    AutoBankReconciliationUseCase,
    BankPayment,
)
from src.domain.entities import Tenant
from src.infrastructure.persistence.repositories.postgresql_settlement_repository import (
    PostgreSQLSettlementRepository,
)

router = APIRouter(prefix="/bank-reconciliation", tags=["Bank Reconciliation"])


class BankPaymentPayload(BaseModel):
    payment_date: date = Field(..., description="Data do crédito bancário")
    amount: Decimal = Field(..., description="Valor recebido")
    reference: str | None = Field(None, description="Identificador opcional do banco")


class AutoReconciliationResponse(BaseModel):
    matched: List[dict]
    unmatched: List[dict]


@router.post("/auto-match", response_model=AutoReconciliationResponse)
async def auto_match_bank_payments(
    payload: List[BankPaymentPayload],
    tenant: Tenant = Depends(get_current_tenant),
    session: AsyncSession = Depends(get_db_session),
):
    repository = PostgreSQLSettlementRepository(session)
    use_case = AutoBankReconciliationUseCase(repository)

    request = AutoBankReconciliationRequest(
        tenant_id=tenant.id,
        payments=[
            BankPayment(
                payment_date=item.payment_date,
                amount=item.amount,
                reference=item.reference,
            )
            for item in payload
        ],
    )

    result = await use_case.execute(request)
    return AutoReconciliationResponse(
        matched=[
            {
                "payment_date": match.payment_date,
                "amount": float(match.amount),
                "settlement_id": match.settlement_id,
                "expected_date": match.expected_date,
            }
            for match in result.matched
        ],
        unmatched=[
            {
                "payment_date": payment.payment_date,
                "amount": float(payment.amount),
                "reference": payment.reference,
            }
            for payment in result.unmatched
        ],
    )


__all__ = ["router"]
