"""SQLAlchemy-backed notification repository."""

from __future__ import annotations

from datetime import datetime
from typing import List
from uuid import UUID

from sqlalchemy import Select, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from src.domain.entities import Notification
from src.domain.repositories import INotificationRepository
from ..mappers import NotificationMapper
from ..models import NotificationModel

logger = structlog.get_logger(__name__)


class NotificationRepository(INotificationRepository):
    """Persist notifications using an AsyncSession."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._mapper = NotificationMapper()
        self._logger = logger.bind(repository="NotificationRepository")

    async def create(self, notification: Notification) -> None:
        model = NotificationModel(
            id=notification.id,
            tenant_id=UUID(notification.tenant_id),
            title=notification.title,
            message=notification.message,
            priority=notification.priority,
            action_url=notification.action_url,
            is_read=notification.is_read,
            created_at=notification.created_at,
            read_at=notification.read_at,
        )
        self._session.add(model)
        await self._session.flush()

        self._logger.debug(
            "notification_created",
            notification_id=str(notification.id),
            tenant_id=notification.tenant_id,
            priority=notification.priority,
        )

    async def find_all(self, tenant_id: str) -> List[Notification]:
        stmt: Select[NotificationModel] = (
            select(NotificationModel)
            .where(NotificationModel.tenant_id == UUID(tenant_id))
            .order_by(NotificationModel.created_at.desc())
        )
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [self._mapper.to_entity(model) for model in models]

    async def find_unread(self, tenant_id: str) -> List[Notification]:
        stmt: Select[NotificationModel] = (
            select(NotificationModel)
            .where(
                NotificationModel.tenant_id == UUID(tenant_id),
                NotificationModel.is_read.is_(False),
            )
            .order_by(NotificationModel.created_at.desc())
        )
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [self._mapper.to_entity(model) for model in models]

    async def mark_as_read(self, notification_id: str) -> None:
        stmt = (
            update(NotificationModel)
            .where(NotificationModel.id == UUID(notification_id))
            .values(is_read=True, read_at=datetime.utcnow())
        )
        await self._session.execute(stmt)

        self._logger.debug(
            "notification_marked_read",
            notification_id=notification_id,
        )

    async def count_unread(self, tenant_id: str) -> int:
        stmt = (
            select(func.count(NotificationModel.id))
            .where(
                NotificationModel.tenant_id == UUID(tenant_id),
                NotificationModel.is_read.is_(False),
            )
        )
        result = await self._session.execute(stmt)
        count = result.scalar_one()
        return int(count or 0)


__all__ = ["NotificationRepository"]
