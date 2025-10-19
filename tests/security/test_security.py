"""Security regression tests covering critical controls."""

from __future__ import annotations

from typing import Any, Dict

import pytest
from fastapi.testclient import TestClient

from src.api.gateway import check_rate_limit


@pytest.fixture
def api_client(monkeypatch: pytest.MonkeyPatch) -> TestClient:
    from src.main import app

    async def _noop(*_: Any, **__: Any) -> None:
        return None

    monkeypatch.setattr("src.infrastructure.database.init_database_pool", _noop)
    monkeypatch.setattr("src.infrastructure.cache.init_redis_pool", _noop)
    monkeypatch.setattr("src.infrastructure.database.close_database_pool", _noop)
    monkeypatch.setattr("src.infrastructure.cache.close_redis_pool", _noop)

    with TestClient(app) as client:
        yield client


@pytest.mark.security
@pytest.mark.critical
def test_security_headers_present(api_client: TestClient) -> None:
    response = api_client.get("/api/v1/health")
    assert response.status_code == 200

    headers = response.headers
    assert headers.get("X-Content-Type-Options") == "nosniff"
    assert headers.get("X-Frame-Options") in {"DENY", "SAMEORIGIN"}
    assert headers.get("Strict-Transport-Security") == "max-age=63072000; includeSubDomains"
    assert headers.get("Server") == "ConciliaAI"


@pytest.mark.security
@pytest.mark.critical
def test_sql_injection_payload_rejected(api_client: TestClient) -> None:
    malicious_payload = {
        "start_date": "2025-01-01'; DROP TABLE sales; --",
        "end_date": "2025-01-31",
        "auto_approve": True,
    }
    response = api_client.post("/api/v1/reconciliation/execute", json=malicious_payload)
    assert response.status_code in {400, 422}


class _FakeRedis:
    def __init__(self) -> None:
        self._store: Dict[str, int] = {}

    async def get(self, key: str) -> int | None:
        return self._store.get(key)

    async def setex(self, key: str, _ttl: int, value: int) -> None:
        self._store[key] = value

    async def incr(self, key: str) -> None:
        self._store[key] = self._store.get(key, 0) + 1


@pytest.mark.security
@pytest.mark.asyncio
async def test_rate_limit_blocks_after_threshold(monkeypatch: pytest.MonkeyPatch) -> None:
    fake = _FakeRedis()
    monkeypatch.setattr("src.api.gateway.redis_client", fake)

    tenant_id = "tenant-test"
    for _ in range(5):
        allowed = await check_rate_limit(tenant_id, rate_limit=5)
        assert allowed

    blocked = await check_rate_limit(tenant_id, rate_limit=5)
    assert not blocked
