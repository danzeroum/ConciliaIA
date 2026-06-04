"""Governance endpoint exposing the effective reconciliation decision table."""

from __future__ import annotations

from typing import Dict

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import get_current_tenant, get_db_session
from src.application.services.decision_table import load_policy
from src.domain.entities import Tenant
from src.infrastructure.persistence.models import TenantModel

router = APIRouter()


class ReconciliationRules(BaseModel):
    """Effective, per-tenant reconciliation decision table."""

    auto_approval_threshold: float = Field(
        ..., description="Confidence at/above which a match is auto-approved"
    )
    sla_hours: Dict[str, int] = Field(
        ..., description="Hours to resolve a divergence, per severity"
    )


@router.get(
    "/reconciliation-rules",
    response_model=ReconciliationRules,
    summary="Effective reconciliation decision table",
    tags=["Reconciliation"],
)
async def get_reconciliation_rules(
    tenant: Tenant = Depends(get_current_tenant),
    session: AsyncSession = Depends(get_db_session),
) -> ReconciliationRules:
    """Return the auto-approval/SLA rules in effect for the tenant.

    Defaults come from the embedded decision table and can be overridden per
    tenant via ``tenant.features['reconciliation_policy']``.
    """
    row = (
        await session.execute(select(TenantModel.features).where(TenantModel.id == tenant.id))
    ).scalar_one_or_none()

    policy = load_policy(row if isinstance(row, dict) else None)
    return ReconciliationRules(**policy.as_table())


__all__ = ["router"]
