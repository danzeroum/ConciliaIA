"""Shared request-path classification used by the API middlewares.

The application image serves both the JSON API and the static SPA from the same
origin. The middlewares therefore need a single, consistent notion of which
paths represent the *protected API surface* (JWT + tenant + rate limiting) and
which are public (auth endpoints, health checks, docs, and the static frontend
assets / client-side routes).

The API is fully versioned under ``/api/v1`` — including authentication
(``/api/v1/auth/*``). Authentication endpoints are public (no token required)
but are still rate limited to slow down credential stuffing.
"""

from __future__ import annotations

# Paths under ``/api`` that must remain reachable without authentication.
_AUTH_PREFIX = "/api/v1/auth/"
_PUBLIC_API_PATHS = {"/api/v1/health"}
_HEALTH_PATHS = {"/health", "/api/v1/health"}


def is_protected_api(path: str) -> bool:
    """Return True for API paths that require an authenticated tenant context."""
    normalized = path.rstrip("/") or "/"
    if normalized in _PUBLIC_API_PATHS:
        return False
    if path.startswith(_AUTH_PREFIX) or normalized == _AUTH_PREFIX.rstrip("/"):
        return False
    return path.startswith("/api/")


def is_rate_limited(path: str) -> bool:
    """Return True for paths that should be subject to rate limiting.

    The whole ``/api`` surface (including the public auth endpoints) is
    throttled; health checks and the static frontend are exempt so neither
    uptime probes nor a first page load (many JS chunks) are ever blocked.
    """
    normalized = path.rstrip("/") or "/"
    if normalized in _HEALTH_PATHS:
        return False
    return path.startswith("/api/")


__all__ = ["is_protected_api", "is_rate_limited"]
