"""Interface for acquirer transaction aggregation operations."""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date
from typing import List

from src.domain.entities import AcquirerTransaction, TransactionStatus


class IAcquirerTransactionRepository(ABC):
    """Repository contract focused on settlement-driven queries."""

    @abstractmethod
    async def find_by_status_and_date_range(
        self,
        tenant_id: str,
        status: TransactionStatus,
        start_date: date,
        end_date: date,
    ) -> List[AcquirerTransaction]:
        """Return transactions filtered by settlement status within a date range."""
        raise NotImplementedError

    @abstractmethod
    async def find_by_date_range(
        self,
        tenant_id: str,
        start_date: date,
        end_date: date,
    ) -> List[AcquirerTransaction]:
        """Return transactions that occurred within the provided interval."""
        raise NotImplementedError

    @abstractmethod
    async def find_delayed_settlements(
        self,
        tenant_id: str,
        cutoff_date: date,
    ) -> List[AcquirerTransaction]:
        """Return transactions whose settlement date is past the provided cutoff."""
        raise NotImplementedError

    @abstractmethod
    async def find_chargebacks(
        self,
        tenant_id: str,
        start_date: date,
        end_date: date,
    ) -> List[AcquirerTransaction]:
        """Return chargeback transactions within the given period."""
        raise NotImplementedError
