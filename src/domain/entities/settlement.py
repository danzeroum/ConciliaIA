"""Settlement entity representing merchant payouts."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from enum import Enum
from typing import Optional

from src.domain.value_objects import Money


class SettlementStatus(str, Enum):
    """Settlement payment status."""

    PENDING = "pending"
    PAID = "paid"
    DELAYED = "delayed"


@dataclass
class Settlement:
    """Represents the payment of a transaction to the merchant."""

    id: str
    transaction_id: str
    tenant_id: str
    expected_date: date
    net_amount: Money
    actual_date: Optional[date] = None
    status: SettlementStatus = SettlementStatus.PENDING
    created_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self) -> None:
        if self.actual_date and self.actual_date < self.expected_date:
            raise ValueError("Actual settlement date cannot be before expected date")

        if self.actual_date:
            object.__setattr__(self, "status", SettlementStatus.PAID)
        elif date.today() > self.expected_date:
            object.__setattr__(self, "status", SettlementStatus.DELAYED)

    @property
    def delay_days(self) -> int:
        if self.status != SettlementStatus.DELAYED:
            return 0
        reference = self.actual_date or date.today()
        return (reference - self.expected_date).days

    @property
    def is_paid(self) -> bool:
        return self.status == SettlementStatus.PAID

    @property
    def is_delayed(self) -> bool:
        return self.status == SettlementStatus.DELAYED

    def __str__(self) -> str:  # pragma: no cover - trivial
        return f"Settlement({self.transaction_id}, {self.status})"
