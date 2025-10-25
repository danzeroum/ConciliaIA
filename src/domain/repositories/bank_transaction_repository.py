"""Repository contract for bank statement transactions."""

from __future__ import annotations

from abc import ABC, abstractmethod

from src.domain.entities import BankTransaction


class IBankTransactionRepository(ABC):
    """Defines persistence operations for bank transactions."""

    @abstractmethod
    async def create(self, transaction: BankTransaction) -> BankTransaction:
        """Persist a single bank transaction and return the stored entity."""
        raise NotImplementedError
