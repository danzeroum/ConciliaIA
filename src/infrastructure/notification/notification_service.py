"""Centralised notification delivery service."""

from __future__ import annotations

from typing import Optional

import structlog

from src.domain.entities import Notification
from src.domain.repositories import INotificationRepository

logger = structlog.get_logger(__name__)


class NotificationService:
    """Persist notifications and fan out to additional channels when available."""

    def __init__(
        self,
        notification_repo: INotificationRepository,
        *,
        email_enabled: bool = False,
        whatsapp_enabled: bool = False,
    ) -> None:
        self._notifications = notification_repo
        self._email_enabled = email_enabled
        self._whatsapp_enabled = whatsapp_enabled

    async def send(
        self,
        *,
        tenant_id: str,
        title: str,
        message: str,
        priority: str = "info",
        action_url: Optional[str] = None,
    ) -> None:
        """Persist an in-app notification. Future channels can hook into this method."""

        notification = Notification.create(
            tenant_id=tenant_id,
            title=title,
            message=message,
            priority=priority,
            action_url=action_url,
        )

        await self._notifications.create(notification)

        logger.info(
            "notifications.sent",
            tenant_id=tenant_id,
            title=title,
            priority=priority,
            email_enabled=self._email_enabled,
            whatsapp_enabled=self._whatsapp_enabled,
        )

        # Reserved for future fan-out to other channels.


__all__ = ["NotificationService"]
