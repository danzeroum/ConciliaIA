"""Dependency wiring for FastAPI routes - Updated with PostgreSQL."""

from __future__ import annotations

from fastapi import Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.services import AnomalyDetectionService, MatchingService
from src.application.strategies import ExactMatcher, FuzzyMatcher, InstallmentMatcher, MLMatcher
from src.application.use_cases.reconcile_transactions import ReconcileTransactionsUseCase
from src.domain.entities import Tenant
from src.infrastructure.persistence.database import Database
from src.infrastructure.persistence.repositories.postgresql_divergence_repository import (
    PostgreSQLDivergenceRepository,
)
from src.infrastructure.persistence.repositories.postgresql_match_repository import PostgreSQLMatchRepository
from src.infrastructure.persistence.repositories.postgresql_sale_repository import PostgreSQLSaleRepository
from src.infrastructure.persistence.repositories.postgresql_transaction_repository import (
    PostgreSQLTransactionRepository,
)

# Global database instance (initialized in main.py)
database: Database | None = None


async def get_db_session() -> AsyncSession:
    """Get database session."""
    if database is None:
        raise HTTPException(status_code=500, detail="Database not initialized")

    async for session in database.get_session():
        yield session


async def get_current_tenant(request: Request) -> Tenant:
    """Retrieve the current tenant from the request context."""
    tenant = getattr(request.state, "tenant", None)
    if tenant is None:
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
    session: AsyncSession = Depends(get_db_session),
    _tenant: Tenant = Depends(get_current_tenant),
) -> ReconcileTransactionsUseCase:
    """Create the reconciliation use case with PostgreSQL repositories."""

    sale_repo = PostgreSQLSaleRepository(session)
    transaction_repo = PostgreSQLTransactionRepository(session)
    match_repo = PostgreSQLMatchRepository(session)
    divergence_repo = PostgreSQLDivergenceRepository(session)

    matching_service = MatchingService(
        exact_matcher=ExactMatcher(),
        fuzzy_matcher=FuzzyMatcher(),
        ml_matcher=MLMatcher(),
        installment_matcher=InstallmentMatcher(),
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


__all__ = ["get_current_tenant", "get_reconciliation_use_case", "get_db_session", "database"]
