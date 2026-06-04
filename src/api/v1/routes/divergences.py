"""Divergences API routes backed by the divergence repository."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import get_current_tenant, get_db_session
from src.domain.entities import Divergence, DivergenceStatus, Severity
from src.domain.entities import Tenant
from src.infrastructure.persistence.repositories.postgresql_divergence_repository import (
    PostgreSQLDivergenceRepository,
)

router = APIRouter()


class DivergenceItem(BaseModel):
    """Representation of a divergence record (aligned with the frontend type)."""

    id: str = Field(..., description="Identifier of the divergence")
    tenant_id: str = Field(..., description="Tenant identifier")
    type: str = Field(..., description="Type of divergence")
    sale_id: Optional[str] = Field(None, description="Related sale identifier")
    transaction_id: Optional[str] = Field(None, description="Related transaction identifier")
    severity: str = Field(..., description="Severity level")
    amount_at_risk: Decimal = Field(..., description="Amount at risk in BRL")
    variance_percent: Optional[float] = Field(None, description="Variance percentage")
    status: str = Field(..., description="Lifecycle status")
    detected_at: datetime = Field(..., description="Detection timestamp")
    resolved_at: Optional[datetime] = Field(None, description="Resolution timestamp")
    resolution: Optional[str] = Field(None, description="Resolution notes")
    notified: bool = Field(False, description="Whether the divergence was notified")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Extra metadata")


class DivergencesListResponse(BaseModel):
    """Paginated list of divergences."""

    items: List[DivergenceItem]
    total: int
    page: int
    page_size: int
    total_pages: int


class ResolveDivergenceRequest(BaseModel):
    """Payload for resolving a divergence."""

    resolution: str = Field(..., description="Resolution summary")
    notes: Optional[str] = Field(None, description="Additional notes")


def get_divergence_repository(
    db_session: AsyncSession = Depends(get_db_session),
) -> PostgreSQLDivergenceRepository:
    return PostgreSQLDivergenceRepository(db_session)


def _to_item(divergence: Divergence) -> DivergenceItem:
    """Map a domain ``Divergence`` to the API representation."""
    expected = divergence.expected_value.amount if divergence.expected_value else None
    actual = divergence.actual_value.amount if divergence.actual_value else None
    difference = divergence.difference

    if difference is not None:
        amount_at_risk = difference.amount
    elif expected is not None:
        amount_at_risk = expected
    elif actual is not None:
        amount_at_risk = actual
    else:
        amount_at_risk = Decimal("0")

    variance_percent: Optional[float] = None
    if expected and expected != 0 and difference is not None:
        variance_percent = float(abs(difference.amount) / abs(expected) * 100)

    return DivergenceItem(
        id=divergence.id,
        tenant_id=divergence.tenant_id,
        type=getattr(divergence.divergence_type, "value", divergence.divergence_type),
        sale_id=None,
        transaction_id=None,
        severity=getattr(divergence.severity, "value", divergence.severity),
        amount_at_risk=amount_at_risk,
        variance_percent=variance_percent,
        status=getattr(divergence.status, "value", divergence.status),
        detected_at=divergence.detected_at,
        resolved_at=divergence.resolved_at,
        resolution=divergence.notes or divergence.suggested_action,
        notified=False,
        metadata={
            "match_id": divergence.match_id,
            "suggested_action": divergence.suggested_action,
            "resolved_by": divergence.resolved_by,
        },
    )


@router.get(
    "/divergences",
    response_model=DivergencesListResponse,
    summary="List divergences",
    tags=["Divergences"],
)
async def list_divergences(
    tenant: Tenant = Depends(get_current_tenant),
    repository: PostgreSQLDivergenceRepository = Depends(get_divergence_repository),
    status_filter: Optional[DivergenceStatus] = Query(
        None, alias="status", description="Filter by status"
    ),
    type_filter: Optional[str] = Query(None, alias="type", description="Filter by type"),
    severity: Optional[Severity] = Query(None, description="Filter by severity"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=200, description="Page size"),
) -> DivergencesListResponse:
    """Return divergences for the authenticated tenant from the database."""
    items, total = await repository.find_paginated(
        tenant.id,
        status=status_filter,
        divergence_type=type_filter,
        severity=severity,
        page=page,
        page_size=page_size,
    )

    total_pages = (total + page_size - 1) // page_size if page_size else 1

    return DivergencesListResponse(
        items=[_to_item(divergence) for divergence in items],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get(
    "/divergences/{divergence_id}",
    response_model=DivergenceItem,
    summary="Get divergence",
    tags=["Divergences"],
)
async def get_divergence(
    divergence_id: str,
    tenant: Tenant = Depends(get_current_tenant),
    repository: PostgreSQLDivergenceRepository = Depends(get_divergence_repository),
) -> DivergenceItem:
    """Retrieve a single divergence by its identifier."""
    divergence = await repository.find_by_id(tenant.id, divergence_id)
    if divergence is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Divergence not found"
        )
    return _to_item(divergence)


@router.patch(
    "/divergences/{divergence_id}/resolve",
    response_model=DivergenceItem,
    summary="Resolve divergence",
    tags=["Divergences"],
)
async def resolve_divergence(
    divergence_id: str,
    request: ResolveDivergenceRequest,
    tenant: Tenant = Depends(get_current_tenant),
    repository: PostgreSQLDivergenceRepository = Depends(get_divergence_repository),
) -> DivergenceItem:
    """Mark a divergence as resolved."""
    divergence = await repository.find_by_id(tenant.id, divergence_id)
    if divergence is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Divergence not found"
        )

    notes = request.resolution
    if request.notes:
        notes = f"{request.resolution}\n{request.notes}"

    divergence.status = DivergenceStatus.RESOLVED
    divergence.resolved_at = datetime.utcnow()
    divergence.notes = notes

    await repository.save(divergence)

    return _to_item(divergence)
