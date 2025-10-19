"""Percentage value object used for MDR rates."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP


@dataclass(frozen=True)
class Percentage:
    """Represent a fractional percentage value."""

    value: Decimal

    def __post_init__(self) -> None:
        if self.value < Decimal("0") or self.value > Decimal("1"):
            raise ValueError("Percentage must be between 0 and 1")

        quantized = self.value.quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)
        object.__setattr__(self, "value", quantized)

    def as_decimal(self) -> Decimal:
        return self.value

    def as_percentage(self) -> Decimal:
        return (self.value * 100).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    def apply_to(self, amount: "Money") -> "Money":
        from .money import Money

        return Money(amount.amount * self.value, amount.currency)

    def __str__(self) -> str:  # pragma: no cover - trivial
        return f"{self.as_percentage()}%"
