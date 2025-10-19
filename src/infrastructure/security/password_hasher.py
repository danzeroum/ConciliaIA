"""Password hashing utilities using bcrypt."""

from __future__ import annotations

import bcrypt
import structlog

logger = structlog.get_logger(__name__)


class PasswordHasher:
    """Handle password hashing and verification using bcrypt."""

    def __init__(self, rounds: int = 12) -> None:
        self.rounds = rounds
        self.logger = logger.bind(component="PasswordHasher")

    def hash_password(self, password: str) -> str:
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters long")
        salt = bcrypt.gensalt(rounds=self.rounds)
        hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
        self.logger.debug("password_hashed")
        return hashed.decode("utf-8")

    def verify_password(self, password: str, hashed: str) -> bool:
        try:
            result = bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))
            if result:
                self.logger.debug("password_verified")
            else:
                self.logger.warning("password_verification_failed")
            return result
        except Exception as exc:  # pragma: no cover - defensive
            self.logger.error("password_verification_error", error=str(exc))
            return False


__all__ = ["PasswordHasher"]
