"""Domain entities representing the reconciliation core."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import List, Optional


class TransactionStatus(Enum):
    """Represents the lifecycle of a reconciliation transaction."""

    PENDING = "pending"
    MATCHED = "matched"
    DIVERGENT = "divergent"
    RESOLVED = "resolved"


class MatchType(Enum):
    """Types of matching strategies supported by the platform."""

    EXACT = "exact"
    FUZZY_AMOUNT = "fuzzy_amount"
    FUZZY_DATE = "fuzzy_date"
    INSTALLMENT = "installment"
    ML_PREDICTED = "ml_predicted"


class Severity(Enum):
    """Risk level for divergences identified during reconciliation."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass(frozen=True)
class Money:
    """Immutable value object for monetary amounts."""

    amount: Decimal
    currency: str = "BRL"

    def __post_init__(self) -> None:
        if self.amount < 0:
            raise ValueError("Amount cannot be negative")
        if self.currency != "BRL":
            raise ValueError("Only BRL supported")

    def __add__(self, other: "Money") -> "Money":
        if self.currency != other.currency:
            raise ValueError("Cannot add different currencies")
        return Money(self.amount + other.amount, self.currency)

    def __sub__(self, other: "Money") -> "Money":
        if self.currency != other.currency:
            raise ValueError("Cannot subtract different currencies")
        result = self.amount - other.amount
        if result < 0:
            raise ValueError("Resulting amount cannot be negative")
        return Money(result, self.currency)

    def percentage_diff(self, other: "Money") -> Decimal:
        if other.amount == 0:
            return Decimal("100.0")
        return abs((self.amount - other.amount) / other.amount) * 100


@dataclass
class Sale:
    """Represents a sale recorded in the merchant channel."""

    id: str
    tenant_id: str
    nsu: str
    amount: Money
    date: date
    payment_method: str
    authorization_code: Optional[str] = None
    installments: int = 1
    created_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self) -> None:
        if self.date > date.today():
            raise ValueError("Sale date cannot be in the future")
        if self.installments < 1 or self.installments > 12:
            raise ValueError("Installments must be between 1 and 12")

    @property
    def total_amount(self) -> Money:
        return self.amount


@dataclass
class AcquirerTransaction:
    """Represents a transaction reported by the payment acquirer."""

    id: str
    tenant_id: str
    acquirer: str
    nsu: str
    transaction_date: date
    settlement_date: date
    gross_amount: Money
    mdr_fee: Money
    net_amount: Money
    installments: int = 1
    installment_number: Optional[int] = None
    created_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self) -> None:
        if self.gross_amount.amount < self.net_amount.amount:
            raise ValueError("Gross amount must be >= net amount")
        expected_net = self.gross_amount - self.mdr_fee
        if abs(expected_net.amount - self.net_amount.amount) > Decimal("0.01"):
            raise ValueError("Net amount mismatch: gross - mdr != net")


@dataclass
class ReconciliationMatch:
    """Represents the association between a sale and an acquirer transaction."""

    id: str
    tenant_id: str
    sale_id: str
    transaction_id: str
    match_type: MatchType
    confidence: Decimal
    matched_at: datetime = field(default_factory=datetime.utcnow)
    reviewed_by: Optional[str] = None
    approved: bool = False

    def __post_init__(self) -> None:
        if not (Decimal("0") <= self.confidence <= Decimal("1")):
            raise ValueError("Confidence must be between 0 and 1")

    def requires_human_review(self) -> bool:
        return self.confidence < Decimal("0.95")

    def auto_approve(self) -> None:
        if self.requires_human_review():
            raise ValueError("Cannot auto-approve: confidence < 0.95")
        self.approved = True


@dataclass
class Divergence:
    """Represents a divergence identified after reconciliation."""

    id: str
    tenant_id: str
    type: str
    sale_id: Optional[str]
    transaction_id: Optional[str]
    severity: Severity
    amount_at_risk: Money
    detected_at: datetime = field(default_factory=datetime.utcnow)
    resolved_at: Optional[datetime] = None
    resolution: Optional[str] = None

    def days_since_detection(self) -> int:
        return (datetime.utcnow() - self.detected_at).days

    def should_alert(self) -> bool:
        return self.days_since_detection() in {7, 30, 90}

    def calculate_severity(self, variance_percent: Optional[Decimal] = None) -> Severity:
        amount = self.amount_at_risk.amount

        if variance_percent and variance_percent > 20 and amount > 1000:
            return Severity.CRITICAL
        if variance_percent and 10 <= variance_percent <= 20 and amount >= 500:
            return Severity.HIGH
        if variance_percent and 5 <= variance_percent < 10 and amount >= 100:
            return Severity.MEDIUM
        return Severity.LOW


@dataclass
class Tenant:
    """Represents a tenant (merchant) in the ConciliaAI platform."""

    id: str
    org_name: str
    cnpj: str
    tier: str
    active: bool = True
    features: List[str] = field(default_factory=list)
    acquirer_credentials: dict = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)

    def has_feature(self, feature: str) -> bool:
        return feature in self.features
