"""User domain entity."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(slots=True)
class User:
    """User entity representing an authenticated account."""

    id: UUID
    tenant_id: UUID
    email: str
    password_hash: str
    full_name: str
    is_active: bool
    roles: list[str]
    created_at: datetime
    updated_at: datetime


__all__ = ["User"]
