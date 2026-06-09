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
from src.application.use_cases.cielo_conciliator import ImportCieloReportUseCase
from src.application.services.reconciliation_job_service import ReconciliationJobService
from src.application.use_cases.reconcile_transactions import ReconcileTransactionsUseCase
from src.domain.entities import Tenant
from src.infrastructure.acquirers import CieloAgilizaParser, CieloConciliatorClient
from src.infrastructure.persistence.database import Database
from src.infrastructure.persistence.repositories.postgresql_divergence_repository import (
    PostgreSQLDivergenceRepository,
)
from src.infrastructure.persistence.repositories.postgresql_match_repository import PostgreSQLMatchRepository
from src.infrastructure.persistence.repositories.postgresql_sale_repository import PostgreSQLSaleRepository
from src.infrastructure.persistence.repositories.postgresql_transaction_repository import (
    PostgreSQLTransactionRepository,
)
from src.infrastructure.scheduler import AutoImportScheduler
from src.infrastructure.repositories.postgresql_user_repository import PostgreSQLUserRepository
from src.infrastructure.security import (
    JWTHandler,
    LoginAttemptTracker,
    PasswordHasher,
    RateLimiter,
    TokenBlocklist,
)
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
auto_import_scheduler: AutoImportScheduler | None = None
cielo_conciliator_client: CieloConciliatorClient | None = None
reconciliation_job_service: "ReconciliationJobService | None" = None
login_attempt_tracker: "LoginAttemptTracker | None" = None
token_blocklist: "TokenBlocklist | None" = None

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


def get_login_attempt_tracker() -> LoginAttemptTracker:
    if login_attempt_tracker is None:
        raise HTTPException(status_code=500, detail="Login attempt tracker not initialized")
    return login_attempt_tracker


def get_token_blocklist() -> TokenBlocklist:
    if token_blocklist is None:
        raise HTTPException(status_code=500, detail="Token blocklist not initialized")
    return token_blocklist


def get_auto_import_scheduler() -> AutoImportScheduler:
    if auto_import_scheduler is None:
        raise HTTPException(status_code=500, detail="Scheduler not initialized")
    return auto_import_scheduler


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


def get_cielo_conciliator_client() -> CieloConciliatorClient:
    if cielo_conciliator_client is None:
        raise HTTPException(status_code=500, detail="Cielo Conciliator não inicializado")
    return cielo_conciliator_client


async def get_import_cielo_report_use_case(
    session: AsyncSession = Depends(get_db_session),
) -> ImportCieloReportUseCase:
    client = get_cielo_conciliator_client()
    parser = CieloAgilizaParser()
    transaction_repo = PostgreSQLTransactionRepository(session)
    return ImportCieloReportUseCase(
        client=client,
        parser=parser,
        transaction_repo=transaction_repo,
    )


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


async def get_current_tenant_id(user: dict = Depends(get_current_user)) -> str:
    """Return only the tenant identifier for authenticated requests."""

    return user["tenant_id"]


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


def build_reconciliation_use_case(session: AsyncSession) -> ReconcileTransactionsUseCase:
    """Construct the reconciliation use case from a database session.

    Shared by the HTTP dependency and the background reconciliation worker so
    both wire the exact same repositories and services.
    """
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


def get_reconciliation_use_case(
    session: AsyncSession = Depends(get_db_session),
    _tenant: Tenant = Depends(get_current_tenant),
) -> ReconcileTransactionsUseCase:
    return build_reconciliation_use_case(session)


def get_reconciliation_job_service() -> ReconciliationJobService:
    if reconciliation_job_service is None:
        raise HTTPException(
            status_code=500, detail="Reconciliation job service not initialized"
        )
    return reconciliation_job_service


__all__ = [
    "get_current_user",
    "get_current_tenant",
    "get_reconciliation_use_case",
    "get_db_session",
    "get_ingestion_service",
    "get_jwt_handler",
    "get_password_hasher",
    "get_rate_limiter",
    "get_auto_import_scheduler",
    "get_user_repository",
    "get_current_tenant_id",
    "get_cielo_conciliator_client",
    "get_import_cielo_report_use_case",
    "require_roles",
    "database",
    "jwt_handler",
    "password_hasher",
    "rate_limiter",
    "auth_middleware",
    "auto_import_scheduler",
    "cielo_conciliator_client",
]
