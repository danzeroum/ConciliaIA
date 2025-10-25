"""Repository abstraction for import schedules."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterable, Optional

from src.domain.entities import ImportSchedule


class ImportScheduleRepository(ABC):
    """Persistence contract for :class:`ImportSchedule`."""

    @abstractmethod
    async def add(self, schedule: ImportSchedule) -> None:
        """Store a new schedule."""

    @abstractmethod
    async def update(self, schedule: ImportSchedule) -> None:
        """Persist schedule changes."""

    @abstractmethod
    async def get_by_id(self, schedule_id: str) -> Optional[ImportSchedule]:
        """Fetch a schedule by its identifier."""

    @abstractmethod
    async def get_by_tenant(self, tenant_id: str) -> Iterable[ImportSchedule]:
        """Return all schedules belonging to the tenant."""

    @abstractmethod
    async def list_active(self) -> Iterable[ImportSchedule]:
        """List schedules currently active across tenants."""


__all__ = ["ImportScheduleRepository"]
