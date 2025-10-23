"""Integration tests for protected endpoints with authentication."""

from __future__ import annotations

import os
from datetime import date
from decimal import Decimal
from types import SimpleNamespace

import pytest
from httpx import AsyncClient

os.environ.setdefault("SECRET_KEY", "test-secret")

from src.api import dependencies  # noqa: E402  pylint: disable=wrong-import-position
from src.api.dependencies import get_reconciliation_use_case  # noqa: E402  pylint: disable=wrong-import-position
from src.api.main import app  # noqa: E402  pylint: disable=wrong-import-position
from src.infrastructure.security import JWTHandler  # noqa: E402  pylint: disable=wrong-import-position


class _StubReconcileUseCase:
    """Stub use case returning deterministic reconciliation results."""

    async def execute(self, tenant_id: str, start_date: date, end_date: date) -> SimpleNamespace:
        del tenant_id, start_date, end_date
        return SimpleNamespace(
            matches=[],
            divergences=[],
            total_sales=3,
            total_transactions=3,
            matched_count=3,
            unmatched_sales_count=0,
            unmatched_transactions_count=0,
            accuracy=Decimal("1.0"),
            precision=Decimal("1.0"),
            recall=Decimal("1.0"),
        )


@pytest.mark.integration
@pytest.mark.asyncio
class TestProtectedEndpoints:
    """Test protected endpoints require authentication."""

    async def test_access_protected_endpoint_without_token(self) -> None:
        """Test accessing protected endpoint without token returns 403."""
        app.dependency_overrides[get_reconciliation_use_case] = lambda: _StubReconcileUseCase()

        try:
            async with AsyncClient(app=app, base_url="http://test") as client:
                response = await client.post(
                    "/api/v1/reconciliation/execute",
                    json={
                        "start_date": date.today().isoformat(),
                        "end_date": date.today().isoformat(),
                    },
                )
        finally:
            app.dependency_overrides.pop(get_reconciliation_use_case, None)

        assert response.status_code == 403

    async def test_access_protected_endpoint_with_valid_token(self, test_user) -> None:
        """Test accessing protected endpoint with valid token succeeds."""
        app.dependency_overrides[get_reconciliation_use_case] = lambda: _StubReconcileUseCase()
        jwt_handler = JWTHandler(secret_key=os.environ["SECRET_KEY"])
        token = jwt_handler.create_access_token(
            user_id=str(test_user.id),
            tenant_id=str(test_user.tenant_id),
            email=test_user.email,
            roles=[test_user.role],
            jti="jti-123",
        )

        try:
            async with AsyncClient(app=app, base_url="http://test") as client:
                response = await client.post(
                    "/api/v1/reconciliation/execute",
                    headers={"Authorization": f"Bearer {token}"},
                    json={
                        "start_date": date.today().isoformat(),
                        "end_date": date.today().isoformat(),
                    },
                )
        finally:
            app.dependency_overrides.pop(get_reconciliation_use_case, None)

        assert response.status_code == 200

    async def test_rate_limiting(self) -> None:
        """Test rate limiting on endpoints."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            limiter = dependencies.rate_limiter
            if limiter:
                limiter.buckets.clear()

            for index in range(110):  # Exceed 100 req/min limit
                response = await client.post("/auth/logout")

                if index < 100:
                    assert response.status_code == 200
                else:
                    assert response.status_code == 429
