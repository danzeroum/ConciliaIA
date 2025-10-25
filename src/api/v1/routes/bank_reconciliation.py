"""Endpoints for automatic bank reconciliation."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import List

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import (
    get_current_tenant,
    get_current_tenant_id,
    get_db_session,
)
from src.application.use_cases.auto_bank_reconciliation import (
    AutoBankReconciliationRequest,
    AutoBankReconciliationUseCase,
    BankPayment,
)
from src.application.use_cases.bank_reconciliation import (
    ReconcileBankStatementRequest,
    ReconcileBankStatementUseCase,
)
from src.domain.entities import Tenant
from src.infrastructure.persistence.repositories.acquirer_transaction_repository import (
    AcquirerTransactionRepository,
)
from src.infrastructure.persistence.repositories.postgresql_bank_transaction_repository import (
    PostgreSQLBankTransactionRepository,
)
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


@router.post("/upload-ofx")
async def upload_bank_statement(
    file: UploadFile = File(..., description="Arquivo OFX do banco"),
    bank_account_id: str = "default",
    tenant_id: str = Depends(get_current_tenant_id),
    session: AsyncSession = Depends(get_db_session),
):
    if not file.filename.lower().endswith(".ofx"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Apenas arquivos OFX são aceitos",
        )

    try:
        ofx_content = (await file.read()).decode("utf-8")
    except UnicodeDecodeError as exc:  # pragma: no cover - defensive
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Erro ao ler arquivo. Verifique se é um OFX válido",
        ) from exc

    use_case = ReconcileBankStatementUseCase(
        acquirer_transaction_repo=AcquirerTransactionRepository(session),
        bank_transaction_repo=PostgreSQLBankTransactionRepository(session),
    )

    result = await use_case.execute(
        ReconcileBankStatementRequest(
            tenant_id=tenant_id,
            ofx_content=ofx_content,
            bank_account_id=bank_account_id,
        )
    )

    return {
        "summary_message": result.summary_message,
        "total_transactions": result.total_transactions,
        "matched_count": result.matched_count,
        "unmatched_count": result.unmatched_count,
        "total_matched_amount": float(result.total_matched_amount),
        "matches": result.matches,
    }


__all__ = ["router"]
