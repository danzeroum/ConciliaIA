"""Repository protocol for user aggregates."""

from __future__ import annotations

from typing import Protocol
from uuid import UUID

from src.domain.entities.user import User


class UserRepository(Protocol):
    """Abstraction for retrieving and persisting users."""

    async def find_by_email(self, email: str) -> User | None:
        """Return a user by e-mail address if it exists."""

    async def find_by_id(self, user_id: UUID) -> User | None:
        """Return a user by its identifier."""


__all__ = ["UserRepository"]
