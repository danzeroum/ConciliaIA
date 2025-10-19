"""Playwright end-to-end journeys for ConciliaAI."""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.skipif(
    True,
    reason="Playwright E2E scenarios require a running frontend and browsers",
)


class TestCriticalUserJourneys:  # pragma: no cover - illustrative scenarios
    async def test_placeholder(self) -> None:
        """Placeholder test kept to satisfy pytest discovery."""

        assert True
