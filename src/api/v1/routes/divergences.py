"""Divergences API routes."""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

router = APIRouter()


class DivergenceItem(BaseModel):
    """Representation of a divergence record."""

    id: str = Field(..., description="Identifier of the divergence")
    tenant_id: str = Field(..., description="Tenant identifier")
    type: str = Field(..., description="Type of divergence")
    severity: str = Field(..., description="Severity level")
    amount_at_risk: float = Field(..., description="Amount at risk in BRL")
    detected_at: datetime = Field(..., description="Detection timestamp")
    resolved: bool = Field(False, description="Whether the divergence is resolved")


@router.get(
    "/divergences",
    response_model=List[DivergenceItem],
    summary="List divergences",
    tags=["Divergences"],
)
async def list_divergences(status: Optional[str] = Query(None, description="Filter by status")) -> List[DivergenceItem]:
    """Return a lightweight list of divergences.

    This endpoint currently returns sample data to illustrate the structure of
    the response. Real implementations should query the divergence repository.
    """

    if status not in {None, "open", "resolved"}:
        raise HTTPException(status_code=400, detail="Invalid status filter")

    sample = [
        DivergenceItem(
            id="div-001",
            tenant_id="tenant-123",
            type="missing_transaction",
            severity="high",
            amount_at_risk=850.75,
            detected_at=datetime.utcnow(),
            resolved=False,
        ),
    ]
    return sample
