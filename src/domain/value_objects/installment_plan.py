"""Installment plan value object."""

from __future__ import annotations

from dataclasses import dataclass

from .money import Money


@dataclass(frozen=True)
class InstallmentPlan:
    """Represents a credit card installment plan."""

    current_installment: int
    total_installments: int
    installment_amount: Money

    def __post_init__(self) -> None:
        if self.total_installments < 1 or self.total_installments > 12:
            raise ValueError("Total installments must be between 1 and 12")

        if self.current_installment < 1 or self.current_installment > self.total_installments:
            raise ValueError("Current installment must be within total installments range")

    @property
    def is_complete(self) -> bool:
        return self.current_installment == self.total_installments

    @property
    def total_amount(self) -> Money:
        return self.installment_amount * self.total_installments

    def __str__(self) -> str:  # pragma: no cover - trivial
        return f"{self.current_installment}/{self.total_installments}"
