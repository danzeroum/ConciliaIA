"""Endpoints that expose proactive alerts."""

from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import get_current_tenant, get_db_session
from src.application.services.alert_service import AlertService
from src.domain.entities import Tenant
from src.infrastructure.persistence.repositories.postgresql_settlement_repository import (
    PostgreSQLSettlementRepository,
)
from src.infrastructure.persistence.repositories.postgresql_transaction_repository import (
    PostgreSQLTransactionRepository,
)

router = APIRouter(prefix="/alerts", tags=["Alerts"])


class AlertItem(BaseModel):
    type: str
    severity: str
    title: str
    message: str
    reference_id: str | None = None


@router.get("/proactive", response_model=List[AlertItem])
async def get_proactive_alerts(
    tenant: Tenant = Depends(get_current_tenant),
    session: AsyncSession = Depends(get_db_session),
):
    settlement_repo = PostgreSQLSettlementRepository(session)
    transaction_repo = PostgreSQLTransactionRepository(session)
    service = AlertService(settlement_repo, transaction_repo)
    alerts = await service.generate_alerts(tenant.id)
    return [AlertItem(**alert) for alert in alerts]


__all__ = ["router"]
