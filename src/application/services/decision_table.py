"""Table-driven decisions for auto-approval and SLA (lightweight DMN).

Externalizes the previously hardcoded ``0.95`` auto-approval threshold (and the
divergence SLA) into a small *decision table* expressed as data, with optional
per-tenant overrides stored on ``tenant.features['reconciliation_policy']``.

This is intentionally a lean, embedded decision table — not a full BPMS/DMN
engine. Adopting Camunda/Zeebe-style externalized DMN remains a backlog item to
be considered only when volume and rule complexity justify it.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any, Dict, Mapping, Optional

# The default decision table. Everything here is data so it can be tuned without
# code changes (and overridden per tenant).
DEFAULT_DECISION_TABLE: Dict[str, Any] = {
    # confidence >= threshold -> auto-approve; otherwise -> manual review.
    "auto_approval_threshold": 0.95,
    # SLA (hours to resolve) per divergence severity.
    "sla_hours": {
        "critical": 4,
        "high": 24,
        "medium": 72,
        "low": 168,
    },
}

_POLICY_KEY = "reconciliation_policy"


@dataclass(frozen=True)
class ReconciliationPolicy:
    """Effective reconciliation policy for a tenant."""

    auto_approval_threshold: float = DEFAULT_DECISION_TABLE["auto_approval_threshold"]
    sla_hours: Mapping[str, int] = field(
        default_factory=lambda: dict(DEFAULT_DECISION_TABLE["sla_hours"])
    )

    def decide_auto_approval(self, confidence: float | Decimal) -> str:
        """Return ``"auto_approve"`` or ``"review"`` for a match confidence."""
        return (
            "auto_approve"
            if float(confidence) >= self.auto_approval_threshold
            else "review"
        )

    def sla_for(self, severity: str) -> Optional[int]:
        """Return the SLA in hours for a divergence severity, if defined."""
        return self.sla_hours.get(severity)

    def as_table(self) -> Dict[str, Any]:
        """Serialize the effective decision table (for the governance endpoint)."""
        return {
            "auto_approval_threshold": self.auto_approval_threshold,
            "sla_hours": dict(self.sla_hours),
        }


def load_policy(tenant_features: Optional[Mapping[str, Any]] = None) -> ReconciliationPolicy:
    """Build the effective policy by merging defaults with a tenant override.

    ``tenant_features`` is the tenant's ``features`` JSON; a per-tenant override
    lives under ``features['reconciliation_policy']`` and may set
    ``auto_approval_threshold`` and/or ``sla_hours``.
    """
    threshold = float(DEFAULT_DECISION_TABLE["auto_approval_threshold"])
    sla_hours = dict(DEFAULT_DECISION_TABLE["sla_hours"])

    override: Any = None
    if isinstance(tenant_features, Mapping):
        override = tenant_features.get(_POLICY_KEY)

    if isinstance(override, Mapping):
        raw_threshold = override.get("auto_approval_threshold")
        if isinstance(raw_threshold, (int, float)) and 0 < float(raw_threshold) <= 1:
            threshold = float(raw_threshold)
        raw_sla = override.get("sla_hours")
        if isinstance(raw_sla, Mapping):
            for severity, hours in raw_sla.items():
                if isinstance(hours, int) and hours > 0:
                    sla_hours[severity] = hours

    return ReconciliationPolicy(auto_approval_threshold=threshold, sla_hours=sla_hours)


__all__ = [
    "DEFAULT_DECISION_TABLE",
    "ReconciliationPolicy",
    "load_policy",
]
