"""Entity representing the reconciliation between bank and acquirer transactions."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4


@dataclass(slots=True)
class BankReconciliation:
    """Link between a bank transaction and an acquirer transaction."""

    id: UUID
    tenant_id: str
    bank_transaction_id: UUID
    acquirer_transaction_id: str
    match_confidence: float
    matched_at: datetime = field(default_factory=datetime.utcnow)

    @staticmethod
    def create(
        tenant_id: str,
        bank_transaction_id: UUID,
        acquirer_transaction_id: str,
        match_confidence: float,
    ) -> "BankReconciliation":
        """Create a reconciliation entry."""
        return BankReconciliation(
            id=uuid4(),
            tenant_id=tenant_id,
            bank_transaction_id=bank_transaction_id,
            acquirer_transaction_id=acquirer_transaction_id,
            match_confidence=match_confidence,
        )


__all__ = ["BankReconciliation"]
