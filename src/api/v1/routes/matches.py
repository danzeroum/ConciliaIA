"""Matches API routes backed by the match repository."""

from __future__ import annotations

from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import get_current_tenant, get_db_session
from src.domain.entities import Tenant
from src.infrastructure.persistence.repositories.postgresql_match_repository import (
    PostgreSQLMatchRepository,
)

router = APIRouter()


class MatchItem(BaseModel):
    """Representation of a reconciliation match."""

    id: str = Field(..., description="Match identifier")
    tenant_id: str = Field(..., description="Tenant identifier")
    sale_id: str = Field(..., description="Sale identifier")
    transaction_id: str = Field(..., description="Transaction identifier")
    match_type: str = Field(..., description="Match strategy used")
    confidence: float = Field(..., description="Confidence between 0 and 1")
    validated: bool = Field(..., description="Whether the match is validated")
    matched_at: datetime = Field(..., description="Timestamp of the match")


def get_match_repository(
    db_session: AsyncSession = Depends(get_db_session),
) -> PostgreSQLMatchRepository:
    return PostgreSQLMatchRepository(db_session)


@router.get(
    "/matches",
    response_model=List[MatchItem],
    summary="List recent matches",
    tags=["Matches"],
)
async def list_matches(
    tenant: Tenant = Depends(get_current_tenant),
    repository: PostgreSQLMatchRepository = Depends(get_match_repository),
    limit: int = Query(50, ge=1, le=500),
) -> List[MatchItem]:
    """Return the most recent matches for the authenticated tenant."""
    matches = await repository.find_recent(tenant.id, limit=limit)

    return [
        MatchItem(
            id=match.id,
            tenant_id=match.tenant_id,
            sale_id=match.sale_id,
            transaction_id=match.transaction_id,
            match_type=getattr(match.match_type, "value", match.match_type),
            confidence=float(match.confidence),
            validated=match.validated,
            matched_at=match.matched_at,
        )
        for match in matches
    ]
