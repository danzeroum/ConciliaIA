"""Sliding window rate limiter implementation."""

from __future__ import annotations

import time
from collections import defaultdict, deque
from typing import Deque, Dict

import structlog

logger = structlog.get_logger(__name__)


class RateLimiter:
    """Sliding window rate limiter keyed by identifier."""

    WINDOW_SECONDS = 60.0

    def __init__(self, requests_per_minute: int = 100) -> None:
        self.requests_per_minute = requests_per_minute
        self.buckets: Dict[str, Deque[float]] = defaultdict(deque)
        self.logger = logger.bind(component="RateLimiter")

    def _prune(self, identifier: str, now: float) -> Deque[float]:
        bucket = self.buckets[identifier]
        window_start = now - self.WINDOW_SECONDS
        while bucket and bucket[0] <= window_start:
            bucket.popleft()
        return bucket

    def is_allowed(self, identifier: str) -> bool:
        now = time.time()
        bucket = self._prune(identifier, now)

        if len(bucket) < self.requests_per_minute:
            bucket.append(now)
            return True

        self.logger.warning("rate_limit_exceeded", identifier=identifier)
        return False

    def get_remaining(self, identifier: str) -> int:
        now = time.time()
        bucket = self._prune(identifier, now)
        remaining = self.requests_per_minute - len(bucket)
        return remaining if remaining > 0 else 0


__all__ = ["RateLimiter"]
