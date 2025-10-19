"""Matches API routes."""

from __future__ import annotations

from datetime import datetime
from typing import List

from fastapi import APIRouter, Query
from pydantic import BaseModel, Field

router = APIRouter()


class MatchItem(BaseModel):
    """Representation of a reconciliation match."""

    id: str = Field(..., description="Match identifier")
    tenant_id: str = Field(..., description="Tenant identifier")
    sale_id: str = Field(..., description="Sale identifier")
    transaction_id: str = Field(..., description="Transaction identifier")
    match_type: str = Field(..., description="Match strategy used")
    confidence: float = Field(..., description="Confidence between 0 and 1")
    matched_at: datetime = Field(..., description="Timestamp of the match")


@router.get(
    "/matches",
    response_model=List[MatchItem],
    summary="List recent matches",
    tags=["Matches"],
)
async def list_matches(limit: int = Query(50, ge=1, le=500)) -> List[MatchItem]:
    """Return a sample list of matches ordered by newest first."""

    sample = [
        MatchItem(
            id="match-001",
            tenant_id="tenant-123",
            sale_id="sale-001",
            transaction_id="txn-001",
            match_type="exact",
            confidence=1.0,
            matched_at=datetime.utcnow(),
        )
    ]

    return sample[:limit]
