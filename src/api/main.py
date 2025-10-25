"""FastAPI application entry point."""

from __future__ import annotations

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import structlog

from src.api import dependencies
from src.api.middleware import AuthMiddleware, RateLimitMiddleware, TenantMiddleware
from src.api.routes import auth, cash_flow, notifications
from src.api.v1.routes import (
    alerts,
    auto_import,
    bank_reconciliation,
    cielo_conciliator,
    divergences,
    export,
    health,
    ingestion,
    matches,
    reconciliation,
    reports,
    sales,
    stats,
    transactions,
)
from src.infrastructure.acquirers import CieloConciliatorClient
from src.infrastructure.logging import setup_logging
from src.infrastructure.persistence.database import Database
from src.infrastructure.scheduler import AutoImportScheduler, build_auto_import_runner
from src.infrastructure.security import JWTHandler, PasswordHasher, RateLimiter

setup_logging(environment=os.getenv("ENVIRONMENT", "development"))
logger = structlog.get_logger(__name__)


def _configure_security_components() -> None:
    """Initialise security-related dependencies used across the API."""

    secret_key = os.getenv("SECRET_KEY", "change-me-in-production")
    dependencies.jwt_handler = JWTHandler(secret_key=secret_key)
    dependencies.password_hasher = PasswordHasher(rounds=12)

    limiter_rate = int(
        os.getenv(
            "RATE_LIMIT_REQUESTS_PER_MINUTE",
            os.getenv("RATE_LIMIT_PER_MINUTE", "100"),
        )
    )
    dependencies.rate_limiter = RateLimiter(requests_per_minute=limiter_rate)

    if dependencies.jwt_handler is None:
        raise RuntimeError("JWT handler failed to initialise")
    dependencies.auth_middleware = AuthMiddleware(dependencies.jwt_handler)


_configure_security_components()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("application_startup_started")

    database_url = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://btv_user:btv_password@localhost:5432/conciliaai",
    )
    dependencies.database = Database(database_url)

    if dependencies.database is None:
        raise RuntimeError("Database failed to initialise")

    runner = build_auto_import_runner(dependencies.database.session_factory)
    dependencies.auto_import_scheduler = AutoImportScheduler(
        session_factory=dependencies.database.session_factory,
        runner=runner,
    )
    dependencies.auto_import_scheduler.start()
    await dependencies.auto_import_scheduler.initialise()

    dependencies.cielo_conciliator_client = CieloConciliatorClient()

    logger.info("application_started", environment=os.getenv("ENVIRONMENT"))

    yield

    if dependencies.auto_import_scheduler:
        dependencies.auto_import_scheduler.shutdown()
    if dependencies.cielo_conciliator_client:
        await dependencies.cielo_conciliator_client.aclose()
    if dependencies.database:
        await dependencies.database.close()
    logger.info("application_shutdown")


app = FastAPI(
    title="ConciliaAI API",
    description="Sistema de Reconciliação Financeira com IA",
    version="7.0.0",
    lifespan=lifespan,
)

if dependencies.rate_limiter is None:
    raise RuntimeError("Rate limiter failed to initialise")

app.add_middleware(TenantMiddleware)
app.add_middleware(
    RateLimitMiddleware,
    rate_limiter=dependencies.rate_limiter,
)
# =========================================================================
# CORS configuration
# =========================================================================
# When credentials are included in requests, the wildcard origin "*" cannot be
# used. Explicit origins are required for the preflight request to succeed.
allowed_origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
]

if os.getenv("ENVIRONMENT") == "production":
    prod_origins = [
        origin.strip()
        for origin in os.getenv("CORS_ORIGINS", "").split(",")
        if origin.strip()
    ]
    if prod_origins:
        allowed_origins = prod_origins
        logger.info("cors_production_origins", origins=allowed_origins)

logger.info("cors_configuration", allowed_origins=allowed_origins, credentials=True)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=600,
)

app.include_router(auth.router, prefix="/auth", tags=["authentication"])
app.include_router(cash_flow.router, prefix="/api/v1")
app.include_router(health.router, prefix="/api/v1", tags=["Health"])
app.include_router(auto_import.router, prefix="/api/v1", tags=["Auto Import"])
app.include_router(bank_reconciliation.router, prefix="/api/v1", tags=["Bank Reconciliation"])
app.include_router(cielo_conciliator.router, prefix="/api/v1")
app.include_router(alerts.router, prefix="/api/v1", tags=["Alerts"])
app.include_router(notifications.router, prefix="/api/v1", tags=["Notifications"])
app.include_router(reconciliation.router, prefix="/api/v1", tags=["Reconciliation"])
app.include_router(divergences.router, prefix="/api/v1", tags=["Divergences"])
app.include_router(matches.router, prefix="/api/v1", tags=["Matches"])
app.include_router(sales.router, prefix="/api/v1", tags=["Sales"])
app.include_router(transactions.router, prefix="/api/v1", tags=["Transactions"])
app.include_router(reports.router, prefix="/api/v1", tags=["Reports"])
app.include_router(export.router, prefix="/api/v1", tags=["Exports"])
app.include_router(stats.router, prefix="/api/v1", tags=["Statistics"])
app.include_router(ingestion.router, prefix="/api/v1", tags=["Ingestion"])


@app.middleware("http")
async def apply_security_headers(request, call_next):
    response = await call_next(request)
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "DENY")
    response.headers.setdefault(
        "Strict-Transport-Security", "max-age=63072000; includeSubDomains"
    )
    response.headers["Server"] = "ConciliaAI"
    return response


@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "7.0.0"}


@app.get("/")
async def root():
    return {
        "message": "ConciliaAI API v7.0",
        "docs": "/docs",
        "health": "/health",
        "login": "/auth/login",
    }


__all__ = ["app"]
