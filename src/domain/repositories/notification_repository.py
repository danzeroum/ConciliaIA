"""Notification repository contract."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List

from src.domain.entities import Notification


class INotificationRepository(ABC):
    """Repository interface for storing and querying notifications."""

    @abstractmethod
    async def create(self, notification: Notification) -> None:
        """Persist a notification instance."""

    @abstractmethod
    async def find_all(self, tenant_id: str) -> List[Notification]:
        """Return notifications ordered by most recent first."""

    @abstractmethod
    async def find_unread(self, tenant_id: str) -> List[Notification]:
        """Return unread notifications ordered by recency."""

    @abstractmethod
    async def mark_as_read(self, notification_id: str) -> None:
        """Mark a notification as read."""

    @abstractmethod
    async def count_unread(self, tenant_id: str) -> int:
        """Count unread notifications for the tenant."""


__all__ = ["INotificationRepository"]
