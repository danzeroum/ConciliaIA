"""Unit tests for JWT handler."""

from __future__ import annotations

import pytest

from src.infrastructure.security import JWTHandler


@pytest.mark.unit
class TestJWTHandler:
    """Test JWT handler logic."""

    def test_create_and_verify_access_token(self) -> None:
        handler = JWTHandler(secret_key="test-secret")
        token = handler.create_access_token(
            user_id="user-123",
            tenant_id="tenant-123",
            email="test@example.com",
            roles=["user"],
            jti="jti-123",
        )
        assert isinstance(token, str)
        token_data = handler.verify_token(token)
        assert token_data is not None
        assert token_data.sub == "user-123"
        assert token_data.tenant_id == "tenant-123"
        assert token_data.email == "test@example.com"
        assert "user" in token_data.roles

    def test_verify_expired_token(self) -> None:
        handler = JWTHandler(secret_key="test-secret", access_token_expire_minutes=-1)
        token = handler.create_access_token(
            user_id="user-123",
            tenant_id="tenant-123",
            email="test@example.com",
            roles=["user"],
            jti="jti-123",
        )
        assert handler.verify_token(token) is None

    def test_verify_invalid_token(self) -> None:
        handler = JWTHandler(secret_key="test-secret")
        assert handler.verify_token("invalid.token.here") is None
