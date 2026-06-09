"""In-process tracker for failed login attempts (brute-force mitigation).

Mirrors the architecture of :class:`RateLimiter`: the state lives in this
process. For multi-instance deployments this should be backed by a shared
store (e.g. Redis) — see the scaling backlog in docs/ARCHITECTURE-POSTURE.md.
"""

from __future__ import annotations

import time
from collections import defaultdict
from threading import Lock
from typing import Dict, List


class LoginAttemptTracker:
    """Lock an identity out after too many failed attempts within a window."""

    def __init__(
        self,
        max_attempts: int = 5,
        lockout_seconds: int = 900,
        window_seconds: int = 900,
    ) -> None:
        self.max_attempts = max_attempts
        self.lockout_seconds = lockout_seconds
        self.window_seconds = window_seconds
        self._failures: Dict[str, List[float]] = defaultdict(list)
        self._locked_until: Dict[str, float] = {}
        self._lock = Lock()

    @staticmethod
    def _now() -> float:
        return time.monotonic()

    def seconds_until_unlock(self, key: str) -> int:
        """Remaining lockout seconds for ``key`` (0 when not locked)."""
        with self._lock:
            until = self._locked_until.get(key)
            if until is None:
                return 0
            remaining = until - self._now()
            if remaining <= 0:
                self._locked_until.pop(key, None)
                self._failures.pop(key, None)
                return 0
            return int(remaining) + 1

    def register_failure(self, key: str) -> int:
        """Record a failed attempt.

        Returns the remaining lockout seconds when this failure triggers (or
        sustains) a lock, otherwise 0.
        """
        with self._lock:
            now = self._now()
            recent = [t for t in self._failures[key] if now - t < self.window_seconds]
            recent.append(now)
            self._failures[key] = recent
            if len(recent) >= self.max_attempts:
                self._locked_until[key] = now + self.lockout_seconds
                return self.lockout_seconds
            return 0

    def reset(self, key: str) -> None:
        """Clear all failure state for ``key`` (call on a successful login)."""
        with self._lock:
            self._failures.pop(key, None)
            self._locked_until.pop(key, None)


__all__ = ["LoginAttemptTracker"]
