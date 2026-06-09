"""Parser for Rede's "Gestão de Vendas" REST API (JSON sales responses).

Maps the JSON returned by ``GET /merchant-statement/v1/sales`` into canonical
records and reuses :class:`BaseAcquirerParser` for entity construction (id,
value objects, future-date guarding). The field mapping is verified against a
real sandbox response:

  amount     -> gross amount (valor bruto)
  mdrAmount  -> MDR in BRL  (``mdrFee`` is the rate in %, NOT a BRL amount)
  netAmount  -> net amount (valor líquido)
  saleDate   -> sale date (falls back to ``movementDate`` when absent)
  nsu        -> NSU
  status     -> APPROVED / CANCELLED / ...

The response wraps the rows as ``{"content": {"transactions": [...]},
"cursor": {"hasNextKey": false}}``.
"""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Dict, List, Optional

from src.domain.value_objects import Acquirer

from .base_parser import BaseAcquirerParser


class RedeAPIParser(BaseAcquirerParser):
    """Normalize Rede Gestão de Vendas JSON responses into transactions."""

    # Rede sale status -> domain TransactionStatus value.
    _STATUS_MAP = {
        "APPROVED": "approved",
        "CANCELLED": "cancelled",
        "CANCELED": "cancelled",
        "CHARGEBACK": "chargeback",
        "PENDING": "pending",
        "SETTLED": "settled",
    }

    # The entity only accepts an MDR rate within this band.
    _MIN_RATE = Decimal("0.005")
    _MAX_RATE = Decimal("0.10")

    def __init__(self) -> None:
        super().__init__(Acquirer.REDE)

    def _parse_raw_data(self, raw_data: str | bytes | Dict | List[Dict]) -> List[Dict]:
        if isinstance(raw_data, list):
            return list(raw_data)
        if isinstance(raw_data, dict):
            content = raw_data.get("content")
            if isinstance(content, dict) and isinstance(content.get("transactions"), list):
                return content["transactions"]
            if isinstance(content, list):
                return content
            for key in ("transactions", "sales", "data", "items"):
                value = raw_data.get(key)
                if isinstance(value, list):
                    return value
            if "nsu" in raw_data:  # a single transaction object
                return [raw_data]
        return []

    def _validate_data(self, records: List[Dict]) -> List[Dict]:
        valid: List[Dict] = []
        for record in records:
            if record.get("nsu") in (None, ""):
                continue
            if record.get("amount") is None:
                continue
            if not (record.get("saleDate") or record.get("movementDate")):
                continue
            valid.append(record)
        return valid

    def _normalize_to_canonical(self, record: Dict) -> Dict:
        gross = Decimal(str(record["amount"]))

        net = record.get("netAmount")
        net = Decimal(str(net)) if net is not None else None
        mdr_amount = record.get("mdrAmount")
        mdr_amount = Decimal(str(mdr_amount)) if mdr_amount is not None else None
        if net is None and mdr_amount is not None:
            net = gross - mdr_amount
        if mdr_amount is None and net is not None:
            mdr_amount = gross - net

        mdr_rate = self._mdr_rate(record.get("mdrFee"), mdr_amount, gross)
        transaction_date = self._parse_date(record.get("saleDate") or record.get("movementDate"))

        # Respect the entity invariants so a single odd value does not drop the
        # row: net must be strictly < gross, and mdr_amount must be > 0.
        net_out = net if (net is not None and net < gross) else None
        mdr_out = mdr_amount if (mdr_amount is not None and mdr_amount > 0) else None

        return {
            "nsu": str(record["nsu"]),
            "authorization_code": self._auth_code(record),
            "amount": str(gross.quantize(Decimal("0.01"))),
            "transaction_date": transaction_date,
            "card_brand": "unknown",
            "card_last_4": self._card_last_4(record.get("cardNumber")),
            "mdr_rate": str(mdr_rate) if mdr_rate is not None else None,
            "mdr_amount": str(mdr_out.quantize(Decimal("0.01"))) if mdr_out is not None else None,
            "net_amount": str(net_out.quantize(Decimal("0.01"))) if net_out is not None else None,
            "status": self._STATUS_MAP.get(str(record.get("status", "")).upper(), "approved"),
        }

    def _mdr_rate(
        self, fee: object, mdr_amount: Optional[Decimal], gross: Decimal
    ) -> Optional[Decimal]:
        """Return the MDR rate as a fraction, only when within the accepted band.

        ``mdrFee`` is a percentage (e.g. ``1.84`` == 1.84%); fall back to
        ``mdr_amount / gross`` when the fee is absent.
        """
        rate: Optional[Decimal] = None
        if fee is not None:
            rate = (Decimal(str(fee)) / Decimal("100")).quantize(Decimal("0.0001"))
        elif mdr_amount is not None and gross > 0:
            rate = (mdr_amount / gross).quantize(Decimal("0.0001"))
        if rate is not None and self._MIN_RATE <= rate <= self._MAX_RATE:
            return rate
        return None

    @staticmethod
    def _auth_code(record: Dict) -> Optional[str]:
        auth = record.get("strAuthorizationCode")
        if not auth:
            code = record.get("authorizationCode")
            auth = str(code) if code else None
        if auth is None:
            return None
        normalized = "".join(ch for ch in str(auth) if ch.isalnum())
        return normalized if 4 <= len(normalized) <= 10 else None

    @staticmethod
    def _card_last_4(card_number: object) -> Optional[str]:
        digits = "".join(ch for ch in str(card_number or "") if ch.isdigit())
        return digits[-4:] if len(digits) >= 4 else None

    @staticmethod
    def _parse_date(value: object) -> Optional[date]:
        if isinstance(value, date):
            return value
        if not value:
            return None
        try:
            return datetime.strptime(str(value)[:10], "%Y-%m-%d").date()
        except ValueError:
            return None


__all__ = ["RedeAPIParser"]
