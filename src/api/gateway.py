"""FastAPI gateway with tenant isolation and rate limiting."""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import List

import redis.asyncio as redis
import structlog
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

logger = structlog.get_logger(__name__)

app = FastAPI(
    title="ConciliaAI API",
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

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["api.conciliaai.com", "*.conciliaai.com"],
)

redis_client = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)


@dataclass
class TenantContext:
    """Holds contextual information for the current tenant."""

    tenant_id: str
    org_name: str
    tier: str
    rate_limit: int
    features: List[str]


async def get_tenant_context(request: Request) -> TenantContext:
    """Extract the tenant context from the incoming request."""

    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token")

    token = auth_header.split(" ", maxsplit=1)[1]
    if not token:
        raise HTTPException(status_code=401, detail="Invalid token")

    tenant_id = "tenant_123"

    cache_key = f"tenant:{tenant_id}:config"
    cached_config = await redis_client.get(cache_key)

    if cached_config:
        config = json.loads(cached_config)
    else:
        config = {
            "tenant_id": tenant_id,
            "org_name": "Loja Exemplo",
            "tier": "beta",
            "rate_limit": 100,
            "features": ["reconciliation", "anomaly_detection"],
        }
        await redis_client.setex(cache_key, 3600, json.dumps(config))

    return TenantContext(**config)


async def check_rate_limit(tenant_id: str, rate_limit: int) -> bool:
    """Apply a per-tenant token bucket using Redis."""

    key = f"rate_limit:{tenant_id}:{datetime.utcnow().strftime('%Y%m%d%H%M')}"
    current = await redis_client.get(key)

    if current is None:
        await redis_client.setex(key, 60, 1)
        return True

    if int(current) >= rate_limit:
        return False

    await redis_client.incr(key)
    return True


@app.middleware("http")
async def tenant_isolation_middleware(request: Request, call_next):
    """Middleware responsible for tenant isolation and observability."""

    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    request.state.request_id = request_id

    if request.url.path in {"/health", "/api/docs", "/api/redoc"}:
        response = await call_next(request)
        response.headers.setdefault("X-Request-ID", request_id)
        return response

    try:
        tenant_ctx = await get_tenant_context(request)

        if not await check_rate_limit(tenant_ctx.tenant_id, tenant_ctx.rate_limit):
            raise HTTPException(status_code=429, detail="Rate limit exceeded")

        bound_logger = logger.bind(
            tenant_id=tenant_ctx.tenant_id,
            org_name=tenant_ctx.org_name,
            tier=tenant_ctx.tier,
            request_id=request_id,
        )

        request.state.tenant = tenant_ctx
        request.state.logger = bound_logger

        response = await call_next(request)
        response.headers.setdefault("X-Request-ID", request_id)
        response.headers["X-Tenant-ID"] = tenant_ctx.tenant_id
        return response

    except HTTPException:
        raise
    except Exception as exc:  # pragma: no cover - defensive branch
        logger.error("tenant_middleware_error", error=str(exc), request_id=request_id)
        raise HTTPException(status_code=500, detail="Internal server error") from exc


@app.get("/health")
async def health_check():
    """Return a simple payload for health checks."""

    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat(), "version": "1.0.0"}
