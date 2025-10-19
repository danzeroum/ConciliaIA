"""Unit tests for password hasher."""

from __future__ import annotations

import pytest

from src.infrastructure.security import PasswordHasher


class TestPasswordHasher:
    """Test password hasher."""

    def test_hash_and_verify_password(self) -> None:
        """Test hashing and verifying password."""
        hasher = PasswordHasher()

        password = "SecurePassword123!"
        hashed = hasher.hash_password(password)

        assert isinstance(hashed, str)
        assert len(hashed) > 50
        assert hashed != password  # Hash should be different from password

        # Verify correct password
        assert hasher.verify_password(password, hashed) is True

        # Verify incorrect password
        assert hasher.verify_password("WrongPassword", hashed) is False

    def test_hash_short_password_raises_error(self) -> None:
        """Test that short password raises error."""
        hasher = PasswordHasher()

        with pytest.raises(ValueError, match="at least 8 characters"):
            hasher.hash_password("short")

    def test_different_hashes_for_same_password(self) -> None:
        """Test that same password produces different hashes (due to salt)."""
        hasher = PasswordHasher()

        password = "SamePassword123!"
        hash1 = hasher.hash_password(password)
        hash2 = hasher.hash_password(password)

        assert hash1 != hash2  # Different salts
        assert hasher.verify_password(password, hash1) is True
        assert hasher.verify_password(password, hash2) is True
