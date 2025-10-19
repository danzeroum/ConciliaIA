"""Reconciliation match entity."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import Enum


class MatchType(str, Enum):
    """Types of matching strategies."""

    EXACT = "exact"
    FUZZY_AMOUNT = "fuzzy_amount"
    FUZZY_DATE = "fuzzy_date"
    INSTALLMENT = "installment"
    ML_PREDICTED = "ml_predicted"


@dataclass
class ReconciliationMatch:
    """Association between a sale and an acquirer transaction."""

    id: str
    tenant_id: str
    sale_id: str
    transaction_id: str
    match_type: MatchType
    confidence: Decimal
    matched_at: datetime = field(default_factory=datetime.utcnow)
    validated: bool = False
    validated_by: str | None = None
    validated_at: datetime | None = None

    def __post_init__(self) -> None:
        if self.confidence < Decimal("0.0") or self.confidence > Decimal("1.0"):
            raise ValueError("Confidence must be between 0.0 and 1.0")

        if self.validated and self.confidence < Decimal("0.70"):
            raise ValueError("Validated matches must have confidence >= 0.70")

        if self.confidence >= Decimal("0.95") and not self.validated:
            object.__setattr__(self, "validated", True)
            object.__setattr__(self, "validated_by", "system")
            object.__setattr__(self, "validated_at", datetime.utcnow())

    @property
    def requires_review(self) -> bool:
        return self.confidence < Decimal("0.95")

    @property
    def is_auto_approved(self) -> bool:
        return self.validated and self.validated_by == "system"

    def __str__(self) -> str:  # pragma: no cover - trivial
        return f"Match({self.match_type}, confidence={self.confidence})"
