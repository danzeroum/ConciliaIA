"""Audit middleware — records sensitive mutations to the audit_logs table."""

from __future__ import annotations

from typing import Awaitable, Callable
from uuid import UUID, uuid4

import structlog
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

logger = structlog.get_logger(__name__)

# HTTP methods that modify state and should be audited.
_MUTABLE_METHODS = {"POST", "PUT", "PATCH", "DELETE"}

# Route prefixes that contain sensitive mutations.
_AUDITED_PREFIXES = (
    "/api/v1/reconciliation/execute",
    "/api/v1/divergences",
    "/api/v1/export",
    "/api/v1/reports",
    "/api/v1/ingestion",
    "/api/v1/reconciliation-rules",
    "/api/v1/auto-import",
    "/api/v1/matches",
)


class AuditMiddleware(BaseHTTPMiddleware):
    """Write one audit_logs row per mutable request on sensitive routes.

    Reads user/tenant from the request state populated by JWTContextMiddleware.
    Falls back gracefully when no DB session is available (e.g. startup).
    """

    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        method = request.method
        path = request.url.path

        should_audit = method in _MUTABLE_METHODS and any(
            path.startswith(prefix) for prefix in _AUDITED_PREFIXES
        )

        response = await call_next(request)

        if not should_audit:
            return response

        try:
            await self._write_log(request, path, method, response.status_code)
        except Exception:
            # Audit failures must never break the request flow, but they must
            # be observable instead of silently swallowed.
            logger.warning(
                "audit_log_write_failed", path=path, method=method, exc_info=True
            )

        return response

    @staticmethod
    async def _write_log(
        request: Request,
        path: str,
        method: str,
        status_code: int,
    ) -> None:
        from src.api import dependencies as deps  # local import avoids circular
        from src.infrastructure.persistence.models import AuditLogModel

        if deps.database is None:
            return

        user_id = getattr(request.state, "user_id", "anonymous")
        tenant_id = getattr(request.state, "tenant_id", None)
        if not tenant_id:
            return

        resource_type, resource_id = _parse_resource(path)
        action = f"{method.lower()}:{resource_type}"
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            ip = forwarded.split(",")[0].strip()
        else:
            ip = request.client.host if request.client else None
        user_agent = request.headers.get("User-Agent")
        log_status = "success" if status_code < 400 else "error"

        # Use the ORM (typed columns) instead of raw SQL so UUID/JSONB values
        # are bound with the correct Postgres types and the insert is portable.
        async for session in deps.database.get_session():
            session.add(
                AuditLogModel(
                    id=uuid4(),
                    tenant_id=UUID(str(tenant_id)),
                    user_id=str(user_id),
                    action=action,
                    resource_type=resource_type,
                    resource_id=resource_id,
                    ip_address=ip[:45] if ip else None,
                    user_agent=user_agent[:500] if user_agent else None,
                    status=log_status,
                )
            )
            await session.commit()
            break


def _parse_resource(path: str) -> tuple[str, str]:
    """Extract (resource_type, resource_id) from a URL path."""
    parts = [p for p in path.strip("/").split("/") if p]
    # /api/v1/<resource>/<id>/...
    if len(parts) >= 3:
        return parts[2], parts[3] if len(parts) > 3 else "-"
    if len(parts) == 3:
        return parts[2], "-"
    return path, "-"
