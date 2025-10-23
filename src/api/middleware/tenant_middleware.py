"""Tenant isolation middleware."""

from __future__ import annotations

from fastapi import HTTPException, Request, status
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response
import structlog

logger = structlog.get_logger(__name__)

EXCLUDED_PATHS = (
    "/health",
    "/docs",
    "/openapi.json",
    "/api/v1/health",
    "/api/v1/docs",
    "/api/v1/openapi.json",
    "/api/v1/auth/",
    "/auth/login",
    "/auth/refresh",
    "/auth/logout",
    "/favicon.ico",
)


class TenantMiddleware(BaseHTTPMiddleware):
    """Ensure that requests are scoped to the authenticated tenant."""

    def __init__(self, app) -> None:  # type: ignore[override]
        super().__init__(app)
        self.logger = logger.bind(middleware="TenantMiddleware")

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        path = request.url.path

        if any(path.startswith(prefix) for prefix in EXCLUDED_PATHS):
            return await call_next(request)

        tenant_id = getattr(request.state, "tenant_id", None)
        if not tenant_id:
            self.logger.warning("tenant_validation_failed", path=str(request.url.path))
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Tenant not authorized",
            )

        path_tenant_id = request.path_params.get("tenant_id") if request.path_params else None
        query_tenant_id = request.query_params.get("tenant_id")

        if path_tenant_id and path_tenant_id != tenant_id:
            self.logger.warning(
                "tenant_mismatch",
                authenticated_tenant=tenant_id,
                requested_tenant=path_tenant_id,
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Tenant mismatch",
            )

        if query_tenant_id and query_tenant_id != tenant_id:
            self.logger.warning(
                "tenant_mismatch",
                authenticated_tenant=tenant_id,
                requested_tenant=query_tenant_id,
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Tenant mismatch",
            )

        return await call_next(request)


__all__ = ["TenantMiddleware"]
