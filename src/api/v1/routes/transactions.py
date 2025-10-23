"""API routes for managing acquirer transactions."""

from __future__ import annotations

from datetime import date
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import get_current_tenant, get_db_session
from src.application.services.transaction_service import TransactionService
from src.domain.entities import Tenant
from src.infrastructure.persistence.repositories.postgresql_match_repository import (
    PostgreSQLMatchRepository,
)
from src.infrastructure.persistence.repositories.postgresql_transaction_repository import (
    PostgreSQLTransactionRepository,
)

router = APIRouter()


class CreateTransactionRequest(BaseModel):
    """Payload for creating a transaction."""

    nsu: str = Field(..., description="Transaction NSU")
    acquirer: str = Field(..., description="Acquirer name")
    amount: float = Field(..., gt=0, description="Amount in BRL")
    transaction_date: date = Field(..., description="Transaction date")
    card_brand: str | None = Field(None, description="Card brand")
    authorization_code: str | None = Field(None, description="Authorization code")
    mdr_rate: float | None = Field(None, ge=0, le=100, description="MDR percentage")
    mdr_amount: float | None = Field(None, ge=0, description="MDR amount")
    status: str | None = Field(None, description="Transaction status")


class TransactionResponse(BaseModel):
    """Representation of a transaction resource."""

    id: str
    tenant_id: str
    nsu: str
    acquirer: str
    amount: float
    transaction_date: str
    card_brand: str | None
    authorization_code: str | None
    mdr_rate: float | None
    mdr_amount: float | None
    status: str
    matched: bool
    match_ids: List[str]
    created_at: str


class TransactionsListResponse(BaseModel):
    """Paginated transaction list."""

    items: List[TransactionResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class ImportTransactionsResponse(BaseModel):
    """Response model for transaction CSV import."""

    imported: int
    failed: int
    errors: List[dict] = Field(default_factory=list)


def get_transaction_service(
    db_session: AsyncSession = Depends(get_db_session),
) -> TransactionService:
    repo = PostgreSQLTransactionRepository(db_session)
    return TransactionService(repo)


def get_match_repository(
    db_session: AsyncSession = Depends(get_db_session),
) -> PostgreSQLMatchRepository:
    return PostgreSQLMatchRepository(db_session)


@router.post(
    "/transactions",
    response_model=TransactionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create transaction",
    tags=["Transactions"],
)
async def create_transaction(
    request: CreateTransactionRequest,
    tenant: Tenant = Depends(get_current_tenant),
    service: TransactionService = Depends(get_transaction_service),
    match_repo: PostgreSQLMatchRepository = Depends(get_match_repository),
) -> TransactionResponse:
    """Create a new transaction."""
    transaction = await service.create_transaction(
        tenant_id=tenant.id,
        nsu=request.nsu,
        acquirer=request.acquirer,
        amount=request.amount,
        transaction_date=request.transaction_date,
        card_brand=request.card_brand,
        authorization_code=request.authorization_code,
        mdr_rate=request.mdr_rate,
        mdr_amount=request.mdr_amount,
        status=request.status,
    )

    matches = await match_repo.find_by_transaction(tenant.id, transaction.id)
    match_ids = [match.id for match in matches]

    return TransactionResponse(
        id=transaction.id,
        tenant_id=transaction.tenant_id,
        nsu=str(transaction.nsu),
        acquirer=str(transaction.acquirer),
        amount=float(transaction.amount.amount),
        transaction_date=transaction.transaction_date.isoformat(),
        card_brand=transaction.card_brand,
        authorization_code=str(transaction.authorization_code)
        if getattr(transaction, "authorization_code", None)
        else None,
        mdr_rate=float(transaction.mdr_rate.as_percentage()) if transaction.mdr_rate else None,
        mdr_amount=float(transaction.mdr_amount.amount) if transaction.mdr_amount else None,
        status=transaction.status.value if hasattr(transaction.status, "value") else str(transaction.status),
        matched=bool(match_ids),
        match_ids=match_ids,
        created_at=transaction.created_at.isoformat(),
    )


@router.get(
    "/transactions",
    response_model=TransactionsListResponse,
    summary="List transactions",
    tags=["Transactions"],
)
async def list_transactions(
    tenant: Tenant = Depends(get_current_tenant),
    service: TransactionService = Depends(get_transaction_service),
    match_repo: PostgreSQLMatchRepository = Depends(get_match_repository),
    start_date: date | None = Query(None, description="Filter by start date"),
    end_date: date | None = Query(None, description="Filter by end date"),
    acquirer: str | None = Query(None, description="Filter by acquirer"),
    matched: bool | None = Query(None, description="Filter by match status"),
    nsu: str | None = Query(None, description="Filter by NSU"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Page size"),
) -> TransactionsListResponse:
    """List transactions with optional filters."""
    result = await service.list_transactions(
        tenant_id=tenant.id,
        start_date=start_date,
        end_date=end_date,
        acquirer=acquirer,
        matched=matched,
        nsu=nsu,
        page=page,
        page_size=page_size,
    )

    match_map = {}
    if start_date or end_date:
        matches = await match_repo.find_by_date_range(
            tenant.id,
            start_date or date(1970, 1, 1),
            end_date or date.today(),
        )
    else:
        matches = await match_repo.find_by_date_range(
            tenant.id,
            date(1970, 1, 1),
            date.today(),
        )
    for match in matches:
        match_map.setdefault(match.transaction_id, []).append(match.id)

    items = [
        TransactionResponse(
            id=txn.id,
            tenant_id=txn.tenant_id,
            nsu=str(txn.nsu),
            acquirer=str(txn.acquirer),
            amount=float(txn.amount.amount),
            transaction_date=txn.transaction_date.isoformat(),
            card_brand=txn.card_brand,
            authorization_code=str(txn.authorization_code)
            if getattr(txn, "authorization_code", None)
            else None,
            mdr_rate=float(txn.mdr_rate.as_percentage()) if txn.mdr_rate else None,
            mdr_amount=float(txn.mdr_amount.amount) if txn.mdr_amount else None,
            status=txn.status.value if hasattr(txn.status, "value") else str(txn.status),
            matched=txn.id in match_map,
            match_ids=match_map.get(txn.id, []),
            created_at=txn.created_at.isoformat(),
        )
        for txn in result["items"]
    ]

    total = result["total"]
    total_pages = (total + page_size - 1) // page_size if page_size else 1

    return TransactionsListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get(
    "/transactions/{transaction_id}",
    response_model=TransactionResponse,
    summary="Get transaction",
    tags=["Transactions"],
)
async def get_transaction(
    transaction_id: UUID,
    tenant: Tenant = Depends(get_current_tenant),
    service: TransactionService = Depends(get_transaction_service),
    match_repo: PostgreSQLMatchRepository = Depends(get_match_repository),
) -> TransactionResponse:
    """Retrieve a transaction by identifier."""
    transaction = await service.get_transaction(tenant.id, str(transaction_id))
    if transaction is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found",
        )

    matches = await match_repo.find_by_transaction(tenant.id, transaction.id)
    match_ids = [match.id for match in matches]

    return TransactionResponse(
        id=transaction.id,
        tenant_id=transaction.tenant_id,
        nsu=str(transaction.nsu),
        acquirer=str(transaction.acquirer),
        amount=float(transaction.amount.amount),
        transaction_date=transaction.transaction_date.isoformat(),
        card_brand=transaction.card_brand,
        authorization_code=str(transaction.authorization_code)
        if getattr(transaction, "authorization_code", None)
        else None,
        mdr_rate=float(transaction.mdr_rate.as_percentage()) if transaction.mdr_rate else None,
        mdr_amount=float(transaction.mdr_amount.amount) if transaction.mdr_amount else None,
        status=transaction.status.value if hasattr(transaction.status, "value") else str(transaction.status),
        matched=bool(match_ids),
        match_ids=match_ids,
        created_at=transaction.created_at.isoformat(),
    )


@router.delete(
    "/transactions/{transaction_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete transaction",
    tags=["Transactions"],
    response_model=None,
    
)
async def delete_transaction(
    transaction_id: UUID,
    tenant: Tenant = Depends(get_current_tenant),
    service: TransactionService = Depends(get_transaction_service),
) -> None:
    """Delete a transaction."""
    deleted = await service.delete_transaction(tenant.id, str(transaction_id))
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found",
        )


@router.post(
    "/transactions/import",
    response_model=ImportTransactionsResponse,
    summary="Import transactions via CSV",
    tags=["Transactions"],
)
async def import_transactions(
    file: UploadFile = File(..., description="CSV file"),
    tenant: Tenant = Depends(get_current_tenant),
    service: TransactionService = Depends(get_transaction_service),
) -> ImportTransactionsResponse:
    """Import transactions from CSV."""
    if not file.filename or not file.filename.endswith(".csv"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The uploaded file must be a CSV",
        )

    contents = await file.read()
    result = await service.import_from_csv(tenant.id, contents.decode("utf-8"))
    return ImportTransactionsResponse(**result)


@router.get(
    "/transactions/export/csv",
    summary="Export transactions to CSV",
    tags=["Transactions"],
)
async def export_transactions(
    tenant: Tenant = Depends(get_current_tenant),
    service: TransactionService = Depends(get_transaction_service),
    start_date: date | None = Query(None),
    end_date: date | None = Query(None),
) -> StreamingResponse:
    """Export transactions as CSV."""
    csv_content = await service.export_to_csv(
        tenant_id=tenant.id,
        start_date=start_date,
        end_date=end_date,
    )

    return StreamingResponse(
        iter([csv_content]),
        media_type="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=transactions.csv",
        },
    )


__all__ = ["router"]
