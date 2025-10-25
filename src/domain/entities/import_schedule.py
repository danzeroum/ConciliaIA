"""Entity representing an automated acquirer import schedule."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, time
from typing import Optional
from uuid import uuid4


VALID_SCHEDULE_TYPES = {"daily", "weekly", "monthly"}


def _parse_time(value: str) -> time:
    hour, minute = value.split(":", maxsplit=1)
    return time(hour=int(hour), minute=int(minute))


@dataclass(slots=True)
class ImportSchedule:
    """Configuration describing an automated background import."""

    id: str
    tenant_id: str
    acquirer: str
    schedule_type: str
    time_of_day: str
    days_to_import: int = 1
    credential_hint: str | None = None
    webhook_url: str | None = None
    is_active: bool = True
    last_run_at: Optional[datetime] = None
    next_run_at: Optional[datetime] = None
    error_count: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self) -> None:
        if self.schedule_type not in VALID_SCHEDULE_TYPES:
            raise ValueError(f"Invalid schedule type: {self.schedule_type}")

        _parse_time(self.time_of_day)  # Validate format HH:MM

        if self.days_to_import < 1:
            raise ValueError("days_to_import must be >= 1")

    @property
    def display_name(self) -> str:
        return f"{self.acquirer}::{self.schedule_type}"

    def mark_success(self, timestamp: datetime) -> None:
        self.last_run_at = timestamp
        self.error_count = 0
        self.updated_at = datetime.utcnow()

    def mark_failure(self) -> None:
        self.error_count += 1
        self.updated_at = datetime.utcnow()

    def deactivate(self) -> None:
        self.is_active = False
        self.updated_at = datetime.utcnow()

    @classmethod
    def create(
        cls,
        *,
        tenant_id: str,
        acquirer: str,
        schedule_type: str,
        time_of_day: str,
        days_to_import: int = 1,
        credential_hint: str | None = None,
        webhook_url: str | None = None,
    ) -> "ImportSchedule":
        return cls(
            id=str(uuid4()),
            tenant_id=tenant_id,
            acquirer=acquirer,
            schedule_type=schedule_type,
            time_of_day=time_of_day,
            days_to_import=days_to_import,
            credential_hint=credential_hint,
            webhook_url=webhook_url,
        )


__all__ = ["ImportSchedule", "VALID_SCHEDULE_TYPES"]
