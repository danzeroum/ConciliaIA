"""Installment entity representing a sale installment."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Optional

from src.domain.value_objects import Money


@dataclass
class Installment:
    """Represents a single installment of a multi-installment sale."""

    id: str
    sale_id: str
    tenant_id: str
    current: int
    total: int
    amount: Money
    expected_settlement_date: date
    actual_settlement_date: Optional[date] = None

    def __post_init__(self) -> None:
        if self.total < 1 or self.total > 12:
            raise ValueError("Total installments must be between 1 and 12")

        if self.current < 1 or self.current > self.total:
            raise ValueError("Current installment must be within total range")

    @property
    def is_last(self) -> bool:
        return self.current == self.total

    @property
    def is_settled(self) -> bool:
        return self.actual_settlement_date is not None

    def __str__(self) -> str:  # pragma: no cover - trivial
        return f"Installment({self.current}/{self.total})"
