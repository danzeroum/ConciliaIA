"""Notification entity used for in-app alerts."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4


@dataclass(slots=True)
class Notification:
    """Persisted notification delivered to a tenant."""

    id: UUID
    tenant_id: str
    title: str
    message: str
    priority: str
    action_url: Optional[str]
    is_read: bool
    created_at: datetime
    read_at: Optional[datetime]

    @staticmethod
    def create(
        *,
        tenant_id: str,
        title: str,
        message: str,
        priority: str = "info",
        action_url: Optional[str] = None,
    ) -> "Notification":
        """Instantiate a new unread notification."""

        return Notification(
            id=uuid4(),
            tenant_id=tenant_id,
            title=title,
            message=message,
            priority=priority,
            action_url=action_url,
            is_read=False,
            created_at=datetime.utcnow(),
            read_at=None,
        )


__all__ = ["Notification"]
