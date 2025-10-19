"""Unit tests for rate limiter."""

from __future__ import annotations

import time

from src.infrastructure.security import RateLimiter


class TestRateLimiter:
    """Test rate limiter."""

    def test_allow_requests_within_limit(self) -> None:
        """Test that requests within limit are allowed."""
        limiter = RateLimiter(requests_per_minute=10)

        identifier = "tenant-123"

        # Should allow 10 requests
        for _ in range(10):
            assert limiter.is_allowed(identifier) is True

    def test_block_requests_exceeding_limit(self) -> None:
        """Test that requests exceeding limit are blocked."""
        limiter = RateLimiter(requests_per_minute=5)

        identifier = "tenant-123"

        # Use up all tokens
        for _ in range(5):
            assert limiter.is_allowed(identifier) is True

        # Next request should be blocked
        assert limiter.is_allowed(identifier) is False

    def test_token_refill(self) -> None:
        """Test that tokens refill over time."""
        limiter = RateLimiter(requests_per_minute=60)  # 1 token per second

        identifier = "tenant-123"

        # Use 1 token
        assert limiter.is_allowed(identifier) is True

        # Wait 1 second for refill
        time.sleep(1.1)

        # Should have refilled 1 token
        assert limiter.is_allowed(identifier) is True

    def test_get_remaining_tokens(self) -> None:
        """Test getting remaining tokens."""
        limiter = RateLimiter(requests_per_minute=10)

        identifier = "tenant-123"

        # Initially should have 10 tokens
        assert limiter.get_remaining(identifier) == 10

        # Use 3 tokens
        for _ in range(3):
            limiter.is_allowed(identifier)

        # Should have 7 remaining
        assert limiter.get_remaining(identifier) == 7
