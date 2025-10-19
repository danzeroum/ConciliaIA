"""Token bucket rate limiter implementation."""

from __future__ import annotations

import time
from collections import defaultdict
from typing import Dict

import structlog

logger = structlog.get_logger(__name__)


class RateLimiter:
    """Simple token bucket rate limiter keyed by identifier."""

    def __init__(self, requests_per_minute: int = 100) -> None:
        self.requests_per_minute = requests_per_minute
        self.buckets: Dict[str, dict] = defaultdict(self._create_bucket)
        self.logger = logger.bind(component="RateLimiter")

    def _create_bucket(self) -> dict:
        return {"tokens": float(self.requests_per_minute), "last_update": time.time()}

    def is_allowed(self, identifier: str) -> bool:
        bucket = self.buckets[identifier]
        now = time.time()
        elapsed = now - bucket["last_update"]
        refill = elapsed * (self.requests_per_minute / 60.0)
        bucket["tokens"] = min(self.requests_per_minute, bucket["tokens"] + refill)
        bucket["last_update"] = now
        if bucket["tokens"] >= 1.0:
            bucket["tokens"] -= 1.0
            return True
        self.logger.warning("rate_limit_exceeded", identifier=identifier)
        return False

    def get_remaining(self, identifier: str) -> int:
        bucket = self.buckets[identifier]
        return int(bucket["tokens"])


__all__ = ["RateLimiter"]
