"""API routes for managing sales records."""

from __future__ import annotations

from datetime import date, timedelta
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import get_current_tenant, get_db_session
from src.api.serialization import MoneyAmount
from src.application.services.sales_service import SalesService
from src.domain.entities import Tenant
from src.infrastructure.persistence.repositories.postgresql_match_repository import (
    PostgreSQLMatchRepository,
)
from src.infrastructure.persistence.repositories.postgresql_sale_repository import (
    PostgreSQLSaleRepository,
)

router = APIRouter()


class CreateSaleRequest(BaseModel):
    """Payload for creating a sale."""

    nsu: str = Field(..., description="Unique sale identifier")
    amount: float = Field(..., gt=0, description="Sale amount in BRL")
    sale_date: date = Field(..., description="Sale date")
    payment_method: str = Field(..., description="Payment method")
    installments: int = Field(1, ge=1, le=12, description="Number of installments")
    authorization_code: str | None = Field(None, description="Authorization code")


class UpdateSaleRequest(BaseModel):
    """Payload for updating a sale."""

    amount: float | None = Field(None, gt=0)
    payment_method: str | None = None
    installments: int | None = Field(None, ge=1, le=12)
    authorization_code: str | None = None


class SaleResponse(BaseModel):
    """Representation of a sale resource."""

    id: str
    tenant_id: str
    nsu: str
    amount: MoneyAmount
    sale_date: str
    payment_method: str
    installments: int
    authorization_code: str | None
    matched: bool
    match_ids: List[str]
    created_at: str


class SalesListResponse(BaseModel):
    """Paginated sales list."""

    items: List[SaleResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class ImportSalesResponse(BaseModel):
    """Response model for CSV import."""

    imported: int
    failed: int
    errors: List[dict] = Field(default_factory=list)


def get_sales_service(
    db_session: AsyncSession = Depends(get_db_session),
) -> SalesService:
    sale_repo = PostgreSQLSaleRepository(db_session)
    return SalesService(sale_repo)


def get_match_repository(
    db_session: AsyncSession = Depends(get_db_session),
) -> PostgreSQLMatchRepository:
    return PostgreSQLMatchRepository(db_session)


@router.post(
    "/sales",
    response_model=SaleResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a sale",
    tags=["Sales"],
)
async def create_sale(
    request: CreateSaleRequest,
    tenant: Tenant = Depends(get_current_tenant),
    service: SalesService = Depends(get_sales_service),
    match_repo: PostgreSQLMatchRepository = Depends(get_match_repository),
) -> SaleResponse:
    """Create a new sale for the authenticated tenant."""
    sale = await service.create_sale(
        tenant_id=tenant.id,
        nsu=request.nsu,
        amount=request.amount,
        sale_date=request.sale_date,
        payment_method=request.payment_method,
        installments=request.installments,
        authorization_code=request.authorization_code,
    )

    matches = await match_repo.find_by_sale(tenant.id, sale.id)
    match_ids = [match.id for match in matches]

    return SaleResponse(
        id=sale.id,
        tenant_id=sale.tenant_id,
        nsu=str(sale.nsu),
        amount=sale.amount.amount,
        sale_date=sale.date.isoformat(),
        payment_method=sale.payment_method,
        installments=sale.installments,
        authorization_code=str(sale.authorization_code)
        if getattr(sale, "authorization_code", None)
        else None,
        matched=bool(match_ids),
        match_ids=match_ids,
        created_at=sale.created_at.isoformat(),
    )


@router.get(
    "/sales",
    response_model=SalesListResponse,
    summary="List sales",
    tags=["Sales"],
)
async def list_sales(
    tenant: Tenant = Depends(get_current_tenant),
    service: SalesService = Depends(get_sales_service),
    match_repo: PostgreSQLMatchRepository = Depends(get_match_repository),
    start_date: date | None = Query(None, description="Filter by start date"),
    end_date: date | None = Query(None, description="Filter by end date"),
    payment_method: str | None = Query(None, description="Filter by payment method"),
    matched: bool | None = Query(None, description="Filter by match status"),
    nsu: str | None = Query(None, description="Filter by NSU"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Page size"),
) -> SalesListResponse:
    """List sales applying filters and pagination."""
    result = await service.list_sales(
        tenant_id=tenant.id,
        start_date=start_date,
        end_date=end_date,
        payment_method=payment_method,
        matched=matched,
        nsu=nsu,
        page=page,
        page_size=page_size,
    )

    match_map = {}
    # Avoid an O(history) full scan when no date filter is supplied: default to
    # the last 30 days, which matches the typical reconciliation horizon. When
    # the caller provides a range, honour it (using a 30-day lookback as the
    # lower bound if only ``end_date`` is given).
    default_window = timedelta(days=30)
    if start_date or end_date:
        range_end = end_date or date.today()
        range_start = start_date or (range_end - default_window)
    else:
        range_end = date.today()
        range_start = range_end - default_window

    matches = await match_repo.find_by_date_range(tenant.id, range_start, range_end)
    for match in matches:
        match_map.setdefault(match.sale_id, []).append(match.id)

    items = [
        SaleResponse(
            id=sale.id,
            tenant_id=sale.tenant_id,
            nsu=str(sale.nsu),
            amount=sale.amount.amount,
            sale_date=sale.date.isoformat(),
            payment_method=sale.payment_method,
            installments=sale.installments,
            authorization_code=str(sale.authorization_code)
            if getattr(sale, "authorization_code", None)
            else None,
            matched=sale.id in match_map,
            match_ids=match_map.get(sale.id, []),
            created_at=sale.created_at.isoformat(),
        )
        for sale in result["items"]
    ]

    total = result["total"]
    total_pages = (total + page_size - 1) // page_size if page_size else 1

    return SalesListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get(
    "/sales/{sale_id}",
    response_model=SaleResponse,
    summary="Get sale",
    tags=["Sales"],
)
async def get_sale(
    sale_id: UUID,
    tenant: Tenant = Depends(get_current_tenant),
    service: SalesService = Depends(get_sales_service),
    match_repo: PostgreSQLMatchRepository = Depends(get_match_repository),
) -> SaleResponse:
    """Retrieve a single sale by its identifier."""
    sale = await service.get_sale(tenant.id, str(sale_id))
    if sale is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sale not found")

    matches = await match_repo.find_by_sale(tenant.id, sale.id)
    match_ids = [match.id for match in matches]

    return SaleResponse(
        id=sale.id,
        tenant_id=sale.tenant_id,
        nsu=str(sale.nsu),
        amount=sale.amount.amount,
        sale_date=sale.date.isoformat(),
        payment_method=sale.payment_method,
        installments=sale.installments,
        authorization_code=str(sale.authorization_code)
        if getattr(sale, "authorization_code", None)
        else None,
        matched=bool(match_ids),
        match_ids=match_ids,
        created_at=sale.created_at.isoformat(),
    )


@router.patch(
    "/sales/{sale_id}",
    response_model=SaleResponse,
    summary="Update sale",
    tags=["Sales"],
)
async def update_sale(
    sale_id: UUID,
    request: UpdateSaleRequest,
    tenant: Tenant = Depends(get_current_tenant),
    service: SalesService = Depends(get_sales_service),
    match_repo: PostgreSQLMatchRepository = Depends(get_match_repository),
) -> SaleResponse:
    """Update sale data."""
    sale = await service.update_sale(
        tenant_id=tenant.id,
        sale_id=str(sale_id),
        amount=request.amount,
        payment_method=request.payment_method,
        installments=request.installments,
        authorization_code=request.authorization_code,
    )

    if sale is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sale not found")

    matches = await match_repo.find_by_sale(tenant.id, sale.id)
    match_ids = [match.id for match in matches]

    return SaleResponse(
        id=sale.id,
        tenant_id=sale.tenant_id,
        nsu=str(sale.nsu),
        amount=sale.amount.amount,
        sale_date=sale.date.isoformat(),
        payment_method=sale.payment_method,
        installments=sale.installments,
        authorization_code=str(sale.authorization_code)
        if getattr(sale, "authorization_code", None)
        else None,
        matched=bool(match_ids),
        match_ids=match_ids,
        created_at=sale.created_at.isoformat(),
    )


@router.delete(
    "/sales/{sale_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete sale",
    tags=["Sales"],
    response_model=None,
)
async def delete_sale(
    sale_id: UUID,
    tenant: Tenant = Depends(get_current_tenant),
    service: SalesService = Depends(get_sales_service),
) -> None:
    """Delete a sale."""
    deleted = await service.delete_sale(tenant.id, str(sale_id))
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sale not found")


@router.post(
    "/sales/import",
    response_model=ImportSalesResponse,
    summary="Import sales via CSV",
    tags=["Sales"],
)
async def import_sales(
    file: UploadFile = File(..., description="CSV file"),
    tenant: Tenant = Depends(get_current_tenant),
    service: SalesService = Depends(get_sales_service),
) -> ImportSalesResponse:
    """Import sales from CSV upload."""
    if not file.filename or not file.filename.endswith(".csv"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The uploaded file must be a CSV",
        )

    contents = await file.read()
    result = await service.import_from_csv(tenant.id, contents.decode("utf-8"))
    return ImportSalesResponse(**result)


@router.get(
    "/sales/export/csv",
    summary="Export sales to CSV",
    tags=["Sales"],
)
async def export_sales(
    tenant: Tenant = Depends(get_current_tenant),
    service: SalesService = Depends(get_sales_service),
    start_date: date | None = Query(None),
    end_date: date | None = Query(None),
) -> StreamingResponse:
    """Export sales as a CSV file."""
    csv_content = await service.export_to_csv(
        tenant_id=tenant.id,
        start_date=start_date,
        end_date=end_date,
    )

    return StreamingResponse(
        iter([csv_content]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=sales.csv"},
    )


__all__ = ["router"]
