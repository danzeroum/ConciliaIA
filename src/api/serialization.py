"""Shared serialization helpers for API schemas."""

from __future__ import annotations

from decimal import Decimal
from typing import Annotated

from pydantic import PlainSerializer

# Monetary amounts are kept as ``Decimal`` end-to-end (the database columns are
# ``Numeric(15, 2)`` and the domain uses ``Money``/``Decimal``), so the API
# schema is typed as ``Decimal`` for precision and self-documentation. At the
# JSON boundary the value is emitted as a number rather than a string so the
# existing TypeScript clients (which type money fields as ``number``) keep
# working without changes.
MoneyAmount = Annotated[
    Decimal,
    PlainSerializer(lambda value: float(value), return_type=float, when_used="json"),
]

__all__ = ["MoneyAmount"]
