"""Tenant entity supporting multi-tenancy."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List


class TenantTier(str, Enum):
    """Subscription tier of the tenant."""

    ALPHA = "alpha"
    BETA = "beta"
    GROWTH = "growth"
    SCALE = "scale"
    ENTERPRISE = "enterprise"


@dataclass
class Tenant:
    """Represents an organization onboarded in the platform."""

    id: str
    org_name: str
    cnpj: str
    tier: TenantTier | str
    active: bool = True
    features: List[str] = field(default_factory=list)
    rate_limit: int = 100
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self) -> None:
        if isinstance(self.tier, str):
            object.__setattr__(self, "tier", TenantTier(self.tier))

        digits = "".join(filter(str.isdigit, self.cnpj))
        if len(digits) != 14:
            raise ValueError("CNPJ must have 14 digits")

    def has_feature(self, feature: str) -> bool:
        return feature in self.features

    def __str__(self) -> str:  # pragma: no cover - trivial
        return f"{self.org_name} ({self.tier.value})"
