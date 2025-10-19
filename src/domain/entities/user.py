"""User entity for authentication."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import List


@dataclass
class User:
    """User entity."""

    id: str
    tenant_id: str
    email: str
    password_hash: str
    full_name: str
    roles: List[str] = field(default_factory=list)
    active: bool = True
    email_verified: bool = False
    last_login: datetime | None = None
    failed_login_attempts: int = 0
    account_locked_until: datetime | None = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self) -> None:
        if "@" not in self.email:
            raise ValueError("Invalid email address")
        if not self.password_hash:
            raise ValueError("Password hash is required")

    @property
    def is_locked(self) -> bool:
        if not self.account_locked_until:
            return False
        return datetime.utcnow() < self.account_locked_until

    def has_role(self, role: str) -> bool:
        return role in self.roles

    def has_any_role(self, roles: List[str]) -> bool:
        return any(role in self.roles for role in roles)
