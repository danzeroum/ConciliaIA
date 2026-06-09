"""Notification endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from src.api.dependencies import get_current_tenant_id, get_db_session
from src.infrastructure.persistence.repositories.notification_repository import (
    NotificationRepository,
)

router = APIRouter(prefix="/notifications", tags=["Notifications"])


# Empty path (not "/") so the collection is served at ``/api/v1/notifications``
# without a trailing slash — matching the rest of the API and the frontend
# client. With "/" the SPA catch-all intercepts the no-slash request → 404.
@router.get("")
async def list_notifications(
    unread_only: bool = False,
    tenant_id: str = Depends(get_current_tenant_id),
    db_session=Depends(get_db_session),
):
    """List notifications ordered by recency."""

    repo = NotificationRepository(db_session)

    if unread_only:
        notifications = await repo.find_unread(tenant_id)
    else:
        notifications = await repo.find_all(tenant_id)

    return {
        "notifications": [
            {
                "id": str(notification.id),
                "title": notification.title,
                "message": notification.message,
                "priority": notification.priority,
                "action_url": notification.action_url,
                "is_read": notification.is_read,
                "created_at": notification.created_at.isoformat(),
            }
            for notification in notifications
        ]
    }


@router.post("/{notification_id}/mark-read")
async def mark_notification_as_read(
    notification_id: str,
    tenant_id: str = Depends(get_current_tenant_id),
    db_session=Depends(get_db_session),
):
    """Mark a notification as read."""

    repo = NotificationRepository(db_session)
    await repo.mark_as_read(notification_id)

    return {"status": "read"}


@router.get("/unread-count")
async def get_unread_count(
    tenant_id: str = Depends(get_current_tenant_id),
    db_session=Depends(get_db_session),
):
    """Return unread notification count for the badge indicator."""

    repo = NotificationRepository(db_session)
    count = await repo.count_unread(tenant_id)
    return {"unread_count": count}


__all__ = ["router"]
