"""Sale entity from merchant POS systems."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Optional

from src.domain.value_objects import AuthorizationCode, Money, NSU


@dataclass
class Sale:
    """Sale recorded by the merchant."""

    id: str
    tenant_id: str
    nsu: NSU | str
    amount: Money
    date: date
    payment_method: str
    authorization_code: Optional[AuthorizationCode | str] = None
    installments: int = 1
    created_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self) -> None:
        if isinstance(self.nsu, str):
            object.__setattr__(self, "nsu", NSU(self.nsu))

        if isinstance(self.authorization_code, str) and self.authorization_code:
            object.__setattr__(
                self,
                "authorization_code",
                AuthorizationCode(self.authorization_code),
            )

        if self.date > date.today():
            raise ValueError("Sale date cannot be in the future")

        if self.installments < 1 or self.installments > 12:
            raise ValueError("Installments must be between 1 and 12")

    @property
    def total_amount(self) -> Money:
        return self.amount

    def __str__(self) -> str:  # pragma: no cover - trivial
        return f"Sale({self.id}, {self.amount})"
