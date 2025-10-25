"""Common interfaces for application use cases."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

RequestType = TypeVar("RequestType")
ResponseType = TypeVar("ResponseType")


class UseCase(ABC, Generic[RequestType, ResponseType]):
    """Base contract for application use cases."""

    @abstractmethod
    async def execute(self, request: RequestType) -> ResponseType:
        """Execute the use case with the given request object."""
        raise NotImplementedError
