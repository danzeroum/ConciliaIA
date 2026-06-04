"""Self-describing acquirers endpoint.

Decouples the frontend from a hardcoded acquirer enum by exposing the
registry of supported acquirers and their parser formats.
"""

from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from src.api.dependencies import get_current_tenant
from src.domain.entities import Tenant
from src.infrastructure.acquirers.registry import list_acquirers

router = APIRouter()


class AcquirerInfo(BaseModel):
    """Metadata describing a supported acquirer."""

    id: str = Field(..., description="Acquirer identifier")
    label: str = Field(..., description="Human-friendly name")
    parser_formats: List[str] = Field(
        default_factory=list, description="Import formats with a registered parser"
    )
    supported: bool = Field(..., description="Whether at least one parser is available")


@router.get(
    "/acquirers",
    response_model=List[AcquirerInfo],
    summary="List supported acquirers",
    tags=["Acquirers"],
)
async def get_acquirers(
    _tenant: Tenant = Depends(get_current_tenant),
) -> List[AcquirerInfo]:
    """Return the registry of acquirers and their available parser formats."""
    return [AcquirerInfo(**item) for item in list_acquirers()]


__all__ = ["router"]
