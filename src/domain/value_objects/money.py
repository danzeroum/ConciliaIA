"""Money value object with currency and arithmetic support."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP


@dataclass(frozen=True)
class Money:
    """Immutable representation of a monetary amount."""

    amount: Decimal
    currency: str = "BRL"

    def __post_init__(self) -> None:
        if self.amount < 0:
            raise ValueError("Amount cannot be negative")

        if self.currency != "BRL":
            raise ValueError("Only BRL currency is currently supported")

        quantized = self.amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        object.__setattr__(self, "amount", quantized)

    def __add__(self, other: "Money") -> "Money":
        self._assert_same_currency(other)
        return Money(self.amount + other.amount, self.currency)

    def __sub__(self, other: "Money") -> "Money":
        self._assert_same_currency(other)
        result = self.amount - other.amount
        if result < 0:
            raise ValueError("Resulting amount cannot be negative")
        return Money(result, self.currency)

    def __mul__(self, multiplier: int | float | Decimal) -> "Money":
        return Money(self.amount * Decimal(str(multiplier)), self.currency)

    def __truediv__(self, divisor: int | float | Decimal) -> "Money":
        if divisor == 0:
            raise ValueError("Cannot divide by zero")
        return Money(self.amount / Decimal(str(divisor)), self.currency)

    def percentage_diff(self, other: "Money") -> Decimal:
        if other.amount == 0:
            return Decimal("100.00")
        diff = abs((self.amount - other.amount) / other.amount) * 100
        return diff.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    def _assert_same_currency(self, other: "Money") -> None:
        if self.currency != other.currency:
            raise ValueError("Currency mismatch")

    def __str__(self) -> str:  # pragma: no cover - trivial
        return f"{self.currency} {self.amount:,.2f}"
