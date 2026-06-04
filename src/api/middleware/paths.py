"""Shared request-path classification used by the API middlewares.

The application image serves both the JSON API and the static SPA from the same
origin. The middlewares therefore need a single, consistent notion of which
paths represent the *protected API surface* (JWT + tenant + rate limiting) and
which are public (auth endpoints, health checks, docs, and the static frontend
assets / client-side routes).
"""

from __future__ import annotations

# The only ``/api`` path that must remain reachable without authentication.
_PUBLIC_API_PATHS = {"/api/v1/health"}

# Endpoints that participate in authentication but are themselves public.
_AUTH_PREFIX = "/auth/"


def is_protected_api(path: str) -> bool:
    """Return True for API paths that require an authenticated tenant context."""
    normalized = path.rstrip("/") or "/"
    if normalized in _PUBLIC_API_PATHS:
        return False
    return path.startswith("/api/")


def is_rate_limited(path: str) -> bool:
    """Return True for paths that should be subject to rate limiting.

    Only the API surface and the public auth endpoints are throttled; static
    frontend assets and SPA routes are exempt so a first page load (many JS
    chunks) is never blocked.
    """
    if path == "/health":
        return False
    return is_protected_api(path) or path.startswith(_AUTH_PREFIX)


__all__ = ["is_protected_api", "is_rate_limited"]
