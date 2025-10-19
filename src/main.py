"""ConciliaAI FastAPI application entry point."""

from __future__ import annotations

import time
import uuid
from typing import Awaitable, Callable

import structlog
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response

from src.api.v1.routes import divergences, health, matches, reconciliation
from src.infrastructure import cache, database, logging as logging_setup

logging_setup.setup_logging(environment="production")
logger = structlog.get_logger()

app = FastAPI(
    title="ConciliaAI API",
    description="Sistema Agêntico de Reconciliação Financeira",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://app.conciliaai.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)


@app.middleware("http")
async def logging_middleware(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
):
    """Attach contextual logging information to each request."""

    request_id = str(uuid.uuid4())
    request.state.request_id = request_id

    structlog.contextvars.clear_contextvars()
    structlog.contextvars.bind_contextvars(
        request_id=request_id, method=request.method, path=request.url.path
    )

    start_time = time.time()
    response = await call_next(request)
    duration_ms = (time.time() - start_time) * 1000

    logger.info(
        "http_request",
        status_code=response.status_code,
        duration_ms=round(duration_ms, 2),
    )

    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time"] = f"{duration_ms:.2f}ms"
    _apply_security_headers(response)
    return response


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle uncaught exceptions and return a generic response."""

    logger.error(
        "unhandled_exception",
        error=str(exc),
        error_type=type(exc).__name__,
        path=str(request.url.path),
    )

    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "request_id": getattr(request.state, "request_id", "unknown"),
        },
    )


@app.on_event("startup")
async def startup_event() -> None:
    """Initialize infrastructure resources when the app starts."""

    logger.info("application_starting")
    await database.init_database_pool()
    await cache.init_redis_pool()
    logger.info("application_started")


@app.on_event("shutdown")
async def shutdown_event() -> None:
    """Release infrastructure resources on shutdown."""

    logger.info("application_shutting_down")
    await database.close_database_pool()
    await cache.close_redis_pool()
    logger.info("application_shutdown_complete")


app.include_router(health.router, prefix="/api/v1", tags=["Health"])
app.include_router(reconciliation.router, prefix="/api/v1", tags=["Reconciliation"])
app.include_router(divergences.router, prefix="/api/v1", tags=["Divergences"])
app.include_router(matches.router, prefix="/api/v1", tags=["Matches"])


def _apply_security_headers(response: Response) -> None:
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "DENY")
    response.headers.setdefault(
        "Strict-Transport-Security", "max-age=63072000; includeSubDomains"
    )
    response.headers["Server"] = "ConciliaAI"


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    import uvicorn

    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        workers=2,
        log_config=None,
    )
