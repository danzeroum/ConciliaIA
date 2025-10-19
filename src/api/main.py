"""FastAPI application entry point."""

from __future__ import annotations

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import structlog

from src.api.v1.routes import divergences, health, matches, reconciliation
from src.infrastructure.logging import setup_logging
from src.infrastructure.persistence.database import Database
from . import dependencies

setup_logging(environment=os.getenv("ENVIRONMENT", "development"))
logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan."""
    database_url = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://btv_user:btv_password@localhost:5432/conciliaai",
    )
    dependencies.database = Database(database_url)
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

app.include_router(health.router, prefix="/api/v1", tags=["Health"])
app.include_router(reconciliation.router, prefix="/api/v1", tags=["Reconciliation"])
app.include_router(divergences.router, prefix="/api/v1", tags=["Divergences"])
app.include_router(matches.router, prefix="/api/v1", tags=["Matches"])


@app.middleware("http")
async def apply_security_headers(request, call_next):
    """Attach security headers to all responses."""
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
    """Health check endpoint."""
    return {"status": "healthy", "version": "7.0.0"}


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "ConciliaAI API v7.0",
        "docs": "/docs",
        "health": "/health",
    }


__all__ = ["app"]
