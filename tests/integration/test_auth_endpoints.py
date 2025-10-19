"""Integration tests for authentication endpoints."""

from __future__ import annotations

import os

import pytest
from httpx import AsyncClient

os.environ.setdefault("SECRET_KEY", "test-secret")

from src.api.main import app  # noqa: E402  pylint: disable=wrong-import-position


@pytest.mark.integration
@pytest.mark.asyncio
class TestAuthEndpoints:
    """Test authentication endpoints."""

    async def test_login_success(self) -> None:
        """Test successful login."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/auth/login",
                json={
                    "email": "test@example.com",
                    "password": "SecurePassword123!",
                },
            )

        assert response.status_code == 200
        data = response.json()

        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert data["expires_in"] == 900  # 15 minutes

    async def test_login_invalid_email(self) -> None:
        """Test login with invalid email format."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/auth/login",
                json={
                    "email": "invalid-email",
                    "password": "Password123!",
                },
            )

        assert response.status_code == 422  # Validation error

    async def test_refresh_token(self) -> None:
        """Test token refresh."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            login_response = await client.post(
                "/auth/login",
                json={
                    "email": "test@example.com",
                    "password": "SecurePassword123!",
                },
            )

            refresh_token = login_response.json()["refresh_token"]

            refresh_response = await client.post(
                "/auth/refresh",
                json={"refresh_token": refresh_token},
            )

        assert refresh_response.status_code == 200
        data = refresh_response.json()

        assert "access_token" in data
        assert "refresh_token" in data

    async def test_logout(self) -> None:
        """Test logout."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post("/auth/logout")

        assert response.status_code == 200
        assert response.json()["message"] == "Logged out successfully"
