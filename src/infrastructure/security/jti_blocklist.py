"""In-process blocklist of revoked JWT IDs (``jti``).

Backs refresh-token rotation/reuse-detection and logout revocation. Entries
auto-expire at the token's own expiry so the map stays bounded. State is
per-process — back it with a shared store (Redis) for multi-instance deploys.

NOTE: the module is named ``jti_blocklist`` (not ``token_*``) because the
repository's ``.gitignore`` excludes ``*token*`` paths.
"""

from __future__ import annotations

import time
from threading import Lock
from typing import Dict, Optional


class TokenBlocklist:
    """Track revoked ``jti`` values until their tokens would have expired."""

    def __init__(self) -> None:
        self._revoked: Dict[str, float] = {}
        self._lock = Lock()

    @staticmethod
    def _now() -> float:
        return time.monotonic()

    def revoke(self, jti: Optional[str], ttl_seconds: float) -> None:
        """Revoke ``jti`` for ``ttl_seconds`` (no-op for a falsy jti/ttl)."""
        if not jti or ttl_seconds <= 0:
            return
        with self._lock:
            self._revoked[jti] = self._now() + ttl_seconds
            self._purge_locked()

    def is_revoked(self, jti: Optional[str]) -> bool:
        if not jti:
            return False
        with self._lock:
            expiry = self._revoked.get(jti)
            if expiry is None:
                return False
            if self._now() >= expiry:
                self._revoked.pop(jti, None)
                return False
            return True

    def _purge_locked(self) -> None:
        now = self._now()
        for jti in [j for j, exp in self._revoked.items() if exp <= now]:
            self._revoked.pop(jti, None)


__all__ = ["TokenBlocklist"]
