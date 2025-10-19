"""FastAPI application entry point."""

from __future__ import annotations

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import structlog

from src.api import dependencies
from src.api.middleware import AuthMiddleware, RateLimitMiddleware, TenantMiddleware
from src.api.routes import auth
from src.api.v1.routes import divergences, health, matches, reconciliation
from src.infrastructure.logging import setup_logging
from src.infrastructure.persistence.database import Database
from src.infrastructure.security import JWTHandler, PasswordHasher, RateLimiter

setup_logging(environment=os.getenv("ENVIRONMENT", "development"))
logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("application_startup_started")

    database_url = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://btv_user:btv_password@localhost:5432/conciliaai",
    )
    dependencies.database = Database(database_url)

    secret_key = os.getenv("SECRET_KEY", "change-me-in-production")
    dependencies.jwt_handler = JWTHandler(secret_key=secret_key)
    dependencies.password_hasher = PasswordHasher(rounds=12)
    limiter_rate = int(os.getenv("RATE_LIMIT_PER_MINUTE", "100"))
    dependencies.rate_limiter = RateLimiter(requests_per_minute=limiter_rate)
    dependencies.auth_middleware = AuthMiddleware(dependencies.jwt_handler)

    # Register middlewares that depend on initialised components
    if not getattr(app.state, "tenant_middleware_installed", False):
        app.add_middleware(TenantMiddleware)
        app.state.tenant_middleware_installed = True
    if not getattr(app.state, "rate_limit_middleware_installed", False):
        app.add_middleware(
            RateLimitMiddleware, rate_limiter=dependencies.rate_limiter
        )
        app.state.rate_limit_middleware_installed = True

    logger.info("application_started", environment=os.getenv("ENVIRONMENT"))

    yield

    if dependencies.database:
        await dependencies.database.close()
    logger.info("application_shutdown")


app = FastAPI(
    title="ConciliaAI API",
    description="Sistema de Reconciliação Financeira com IA",
    version="7.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["authentication"])
app.include_router(health.router, prefix="/api/v1", tags=["Health"])
app.include_router(reconciliation.router, prefix="/api/v1", tags=["Reconciliation"])
app.include_router(divergences.router, prefix="/api/v1", tags=["Divergences"])
app.include_router(matches.router, prefix="/api/v1", tags=["Matches"])


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
