"""Dependency wiring for FastAPI routes."""

from __future__ import annotations

from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.services import (
    AnomalyDetectionService,
    IngestionService,
    MatchingService,
)
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
from src.infrastructure.repositories.postgresql_user_repository import PostgreSQLUserRepository
from src.infrastructure.security import JWTHandler, PasswordHasher, RateLimiter
from src.api.middleware import AuthMiddleware

# Global instances initialised during app startup

DatabaseType = Database | None
JWTHandlerType = JWTHandler | None
PasswordHasherType = PasswordHasher | None
RateLimiterType = RateLimiter | None
AuthMiddlewareType = AuthMiddleware | None

database: DatabaseType = None
jwt_handler: JWTHandlerType = None
password_hasher: PasswordHasherType = None
rate_limiter: RateLimiterType = None
auth_middleware: AuthMiddlewareType = None

security = HTTPBearer()


def get_jwt_handler() -> JWTHandler:
    if jwt_handler is None:
        raise HTTPException(status_code=500, detail="JWT handler not initialized")
    return jwt_handler


def get_password_hasher() -> PasswordHasher:
    if password_hasher is None:
        raise HTTPException(status_code=500, detail="Password hasher not initialized")
    return password_hasher


def get_rate_limiter() -> RateLimiter:
    if rate_limiter is None:
        raise HTTPException(status_code=500, detail="Rate limiter not initialized")
    return rate_limiter


async def get_db_session() -> AsyncSession:
    if database is None:
        raise HTTPException(status_code=500, detail="Database not initialized")
    async for session in database.get_session():
        yield session


async def get_ingestion_service(
    session: AsyncSession = Depends(get_db_session),
) -> IngestionService:
    transaction_repo = PostgreSQLTransactionRepository(session)
    return IngestionService(transaction_repo)


async def get_user_repository(
    session: AsyncSession = Depends(get_db_session),
) -> PostgreSQLUserRepository:
    """Provide a PostgreSQL-backed user repository."""

    return PostgreSQLUserRepository(session)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    handler: JWTHandler = Depends(get_jwt_handler),
) -> dict:
    if auth_middleware is None:
        raise HTTPException(status_code=500, detail="Auth middleware not initialized")
    _ = handler
    request = Request(scope={"type": "http"})
    return await auth_middleware(request, credentials)


async def get_current_tenant(user: dict = Depends(get_current_user)) -> Tenant:
    return Tenant(
        id=user["tenant_id"],
        org_name="Authenticated Tenant",
        cnpj="00.000.000/0000-00",
        tier="alpha",
    )


def require_roles(required_roles: list[str]):
    async def _require_roles(user: dict = Depends(get_current_user)) -> dict:
        roles = user.get("roles", [])
        if not any(role in roles for role in required_roles):
            raise HTTPException(
                status_code=403,
                detail=f"Required roles: {', '.join(required_roles)}",
            )
        return user

    return _require_roles


def get_reconciliation_use_case(
    session: AsyncSession = Depends(get_db_session),
    _tenant: Tenant = Depends(get_current_tenant),
) -> ReconcileTransactionsUseCase:
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


__all__ = [
    "get_current_user",
    "get_current_tenant",
    "get_reconciliation_use_case",
    "get_db_session",
    "get_ingestion_service",
    "get_jwt_handler",
    "get_password_hasher",
    "get_rate_limiter",
    "get_user_repository",
    "require_roles",
    "database",
    "jwt_handler",
    "password_hasher",
    "rate_limiter",
    "auth_middleware",
]
