"""Rate limiting middleware."""

from __future__ import annotations

from fastapi import HTTPException, Request, status
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response
import structlog

from src.infrastructure.security import RateLimiter

from .paths import is_rate_limited

logger = structlog.get_logger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Apply a token bucket rate limiter to incoming requests."""

    def __init__(self, app, rate_limiter: RateLimiter) -> None:  # type: ignore[override]
        super().__init__(app)
        self.rate_limiter = rate_limiter
        self.logger = logger.bind(middleware="RateLimitMiddleware")

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Static frontend assets and SPA routes are not throttled so a first
        # page load (many JS chunks) is never blocked.
        if not is_rate_limited(request.url.path):
            return await call_next(request)

        identifier = getattr(request.state, "tenant_id", None)
        if not identifier:
            identifier = request.client.host if request.client else "unknown"

        if not self.rate_limiter.is_allowed(identifier):
            self.logger.warning("rate_limit_exceeded", identifier=identifier)
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Please try again later.",
                headers={
                    "Retry-After": "60",
                    "X-RateLimit-Remaining": "0",
                },
            )

        response = await call_next(request)
        remaining = self.rate_limiter.get_remaining(identifier)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Limit"] = str(self.rate_limiter.requests_per_minute)
        return response


__all__ = ["RateLimitMiddleware"]
