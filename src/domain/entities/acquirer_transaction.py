"""Acquirer transaction entity."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, time
from enum import Enum
from typing import Optional

from src.domain.value_objects import (
    Acquirer,
    AuthorizationCode,
    InstallmentPlan,
    Money,
    NSU,
    Percentage,
)


class TransactionStatus(str, Enum):
    """Lifecycle status for transactions."""

    APPROVED = "approved"
    CANCELLED = "cancelled"
    CHARGEBACK = "chargeback"


@dataclass
class AcquirerTransaction:
    """Transaction reported by the payment acquirer."""

    id: str
    tenant_id: str
    acquirer: Acquirer | str
    nsu: NSU | str
    amount: Money
    transaction_date: date
    authorization_code: Optional[AuthorizationCode | str] = None
    card_brand: Optional[str] = None
    card_last_4: Optional[str] = None
    transaction_time: Optional[time] = None
    installment_plan: Optional[InstallmentPlan] = None
    mdr_rate: Optional[Percentage] = None
    mdr_amount: Optional[Money] = None
    net_amount: Optional[Money] = None
    status: TransactionStatus = TransactionStatus.APPROVED
    created_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self) -> None:
        if isinstance(self.acquirer, str):
            object.__setattr__(self, "acquirer", Acquirer(self.acquirer))

        if isinstance(self.nsu, str):
            object.__setattr__(self, "nsu", NSU(self.nsu))

        if isinstance(self.authorization_code, str) and self.authorization_code:
            object.__setattr__(
                self,
                "authorization_code",
                AuthorizationCode(self.authorization_code),
            )

        if self.transaction_date > date.today():
            raise ValueError("Transaction date cannot be in the future")

        if self.net_amount and self.net_amount.amount >= self.amount.amount:
            raise ValueError("Net amount must be less than gross amount")

        if self.mdr_rate and (self.mdr_rate.value < 0.005 or self.mdr_rate.value > 0.10):
            raise ValueError("MDR rate must be between 0.5% and 10%")

        if self.mdr_amount and not self.net_amount:
            object.__setattr__(self, "net_amount", self.amount - self.mdr_amount)

    @property
    def has_installments(self) -> bool:
        return self.installment_plan is not None

    def __str__(self) -> str:  # pragma: no cover - trivial
        return f"Transaction({self.acquirer}, {self.nsu}, {self.amount})"
