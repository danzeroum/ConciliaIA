"""Populate the request state with the authenticated JWT context.

Historically ``AuthMiddleware`` was only wired as a FastAPI *dependency*, where
it mutated a throwaway ``Request`` object. As a result the real request never
had ``request.state.tenant_id`` populated, and both :class:`TenantMiddleware`
and :class:`RateLimitMiddleware` (which read that attribute) rejected every
authenticated ``/api/v1`` call with ``403 Tenant not authorized``.

This ASGI middleware runs *before* those two middlewares and decodes the bearer
token a single time, attaching the identity to ``request.state``. When a
protected route is reached without a valid token it returns ``401`` so that the
frontend's token-refresh interceptor can kick in.
"""

from __future__ import annotations

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
import structlog

from src.infrastructure.security import JWTHandler

from .paths import is_protected_api

logger = structlog.get_logger(__name__)


class JWTContextMiddleware(BaseHTTPMiddleware):
    """Decode the bearer token and expose the identity on ``request.state``."""

    def __init__(self, app, jwt_handler: JWTHandler) -> None:  # type: ignore[override]
        super().__init__(app)
        self.jwt_handler = jwt_handler
        self.logger = logger.bind(middleware="JWTContextMiddleware")

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        path = request.url.path

        # Only the protected API surface needs an authenticated context. CORS
        # preflight, auth/health endpoints, docs and the static frontend are
        # all served without a token.
        if request.method == "OPTIONS" or not is_protected_api(path):
            return await call_next(request)

        auth_header = request.headers.get("Authorization", "")
        token = None
        if auth_header.lower().startswith("bearer "):
            token = auth_header[7:].strip()

        token_data = self.jwt_handler.verify_token(token) if token else None

        if token_data is None:
            self.logger.warning("jwt_context_missing", path=path)
            request_id = getattr(request.state, "request_id", None)
            return JSONResponse(
                status_code=401,
                content={
                    "detail": "Invalid or expired token",
                    "error_code": "unauthorized",
                    "request_id": request_id,
                },
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Reject tokens whose jti was revoked (logout / refresh rotation).
        from src.api import dependencies as _deps

        blocklist = getattr(_deps, "token_blocklist", None)
        if blocklist is not None and blocklist.is_revoked(token_data.jti):
            self.logger.warning("jwt_revoked", path=path)
            request_id = getattr(request.state, "request_id", None)
            return JSONResponse(
                status_code=401,
                content={
                    "detail": "Token has been revoked",
                    "error_code": "unauthorized",
                    "request_id": request_id,
                },
                headers={"WWW-Authenticate": "Bearer"},
            )

        request.state.user_id = token_data.sub
        request.state.tenant_id = token_data.tenant_id
        request.state.email = token_data.email
        request.state.roles = token_data.roles or []

        return await call_next(request)


__all__ = ["JWTContextMiddleware"]
