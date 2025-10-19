"""Divergence entity for anomaly tracking."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional

from src.domain.value_objects import Money


class DivergenceType(str, Enum):
    """Types of divergences detected during reconciliation."""

    AMOUNT_MISMATCH = "amount_mismatch"
    MDR_VARIANCE = "mdr_variance"
    MISSING_TRANSACTION = "missing_transaction"
    MISSING_SALE = "missing_sale"
    UNAUTHORIZED_CHARGEBACK = "unauthorized_chargeback"
    SETTLEMENT_DELAY = "settlement_delay"
    DUPLICATE_TRANSACTION = "duplicate_transaction"


class Severity(str, Enum):
    """Severity levels for divergences."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class DivergenceStatus(str, Enum):
    """Lifecycle status of divergences."""

    OPEN = "open"
    INVESTIGATING = "investigating"
    RESOLVED = "resolved"
    IGNORED = "ignored"


@dataclass
class Divergence:
    """Divergence detected during reconciliation."""

    id: str
    tenant_id: str
    divergence_type: DivergenceType
    severity: Severity
    match_id: Optional[str] = None
    expected_value: Optional[Money] = None
    actual_value: Optional[Money] = None
    suggested_action: Optional[str] = None
    status: DivergenceStatus = DivergenceStatus.OPEN
    detected_at: datetime = field(default_factory=datetime.utcnow)
    resolved_at: Optional[datetime] = None
    resolved_by: Optional[str] = None
    notes: Optional[str] = None

    def __post_init__(self) -> None:
        if self.status == DivergenceStatus.RESOLVED and not self.resolved_at:
            object.__setattr__(self, "resolved_at", datetime.utcnow())

    @property
    def difference(self) -> Optional[Money]:
        if not self.expected_value or not self.actual_value:
            return None

        diff_amount = abs(self.expected_value.amount - self.actual_value.amount)
        return Money(diff_amount, self.expected_value.currency)

    @property
    def requires_immediate_action(self) -> bool:
        return self.severity == Severity.CRITICAL

    @property
    def days_open(self) -> int:
        reference = self.resolved_at or datetime.utcnow()
        return (reference - self.detected_at).days

    def __str__(self) -> str:  # pragma: no cover - trivial
        return f"Divergence({self.divergence_type}, {self.severity})"
