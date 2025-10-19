"""Dependency wiring for FastAPI routes."""

from __future__ import annotations

from fastapi import Depends, HTTPException, Request

from src.application.services import AnomalyDetectionService, MatchingService
from src.application.strategies import ExactMatcher, FuzzyMatcher, MLMatcher
from src.application.use_cases.reconcile_transactions import ReconcileTransactionsUseCase
from src.domain.entities import Tenant
from src.infrastructure.persistence.in_memory import (
    InMemoryDivergenceRepository,
    InMemoryMatchRepository,
    InMemorySaleRepository,
    InMemoryTransactionRepository,
)


async def get_current_tenant(request: Request) -> Tenant:
    """Retrieve the current tenant from the request context."""

    tenant = getattr(request.state, "tenant", None)
    if tenant is None:
        # In a production environment this would validate JWTs or API keys.
        return Tenant(
            id="tenant-123",
            org_name="Example Tenant",
            cnpj="00.000.000/0000-00",
            tier="alpha",
        )

    if not isinstance(tenant, Tenant):
        raise HTTPException(status_code=500, detail="Invalid tenant context")

    return tenant


def get_reconciliation_use_case(
    _tenant: Tenant = Depends(get_current_tenant),
) -> ReconcileTransactionsUseCase:
    """Create the reconciliation use case with in-memory repositories."""

    sale_repo = InMemorySaleRepository()
    transaction_repo = InMemoryTransactionRepository()
    match_repo = InMemoryMatchRepository()
    divergence_repo = InMemoryDivergenceRepository()

    matching_service = MatchingService(
        exact_matcher=ExactMatcher(),
        fuzzy_matcher=FuzzyMatcher(),
        ml_matcher=MLMatcher(),
    )
    anomaly_service = AnomalyDetectionService()

    return ReconcileTransactionsUseCase(
        sale_repo=sale_repo,
        transaction_repo=transaction_repo,
        match_repo=match_repo,
        divergence_repo=divergence_repo,
        matching_service=matching_service,
        anomaly_service=anomaly_service,
    )


__all__ = ["get_current_tenant", "get_reconciliation_use_case"]
