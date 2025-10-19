"""Stone API response parser."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Dict, List

from src.domain.value_objects import Acquirer

from .base_parser import BaseAcquirerParser


class StoneParser(BaseAcquirerParser):
    """Normalize Stone API responses into domain transactions."""

    def __init__(self) -> None:
        super().__init__(Acquirer.STONE)

    def _parse_raw_data(self, raw_data: List[Dict]) -> List[Dict]:
        return raw_data

    def _validate_data(self, records: List[Dict]) -> List[Dict]:
        valid_records: List[Dict] = []
        for record in records:
            try:
                if not record.get("stone_id"):
                    raise ValueError("Missing stone_id")

                amount_raw = record.get("amount")
                if amount_raw is None:
                    raise ValueError("Missing amount")

                amount = Decimal(str(amount_raw))
                if amount <= 0:
                    raise ValueError("Invalid amount")

                if not record.get("created_at"):
                    raise ValueError("Missing created_at timestamp")

                valid_records.append(record)
            except Exception as exc:
                self.logger.warning(
                    "record_validation_failed", record=record, error=str(exc)
                )
        return valid_records

    def _normalize_to_canonical(self, record: Dict) -> Dict:
        amount = Decimal(str(record["amount"])) / Decimal("100")
        mdr_amount = Decimal(str(record.get("fee_amount", 0))) / Decimal("100")
        net_amount = Decimal(str(record.get("net_amount", 0))) / Decimal("100")
        mdr_rate = ((mdr_amount / amount).quantize(Decimal("0.0001")) if amount > 0 else Decimal("0"))

        timestamp = record["created_at"].replace("Z", "+00:00")
        transaction_date = datetime.fromisoformat(timestamp).date()

        card_info = record.get("card", {})
        card_brand = (card_info.get("brand") or "").lower() or None
        card_last_4 = card_info.get("last_digits")

        return {
            "nsu": record["stone_id"],
            "authorization_code": record.get("authorization_code") or None,
            "amount": str(amount),
            "transaction_date": transaction_date,
            "card_brand": card_brand,
            "card_last_4": card_last_4,
            "mdr_rate": str(mdr_rate),
            "mdr_amount": str(mdr_amount),
            "net_amount": str(net_amount),
            "status": record.get("status", "approved"),
        }


__all__ = ["StoneParser"]
