"""Rede parser for SOAP responses."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Dict, List

from src.domain.value_objects import Acquirer

from .base_parser import BaseAcquirerParser


class RedeParser(BaseAcquirerParser):
    """Normalize Rede SOAP responses into domain transactions."""

    BRAND_MAPPING = {
        "VISA": "visa",
        "MASTERCARD": "mastercard",
        "MASTER": "mastercard",
        "ELO": "elo",
        "AMEX": "amex",
        "DINERS": "diners",
        "HIPERCARD": "hipercard",
    }

    def __init__(self) -> None:
        super().__init__(Acquirer.REDE)

    def _parse_raw_data(self, raw_data: List[Dict]) -> List[Dict]:
        return raw_data

    def _validate_data(self, records: List[Dict]) -> List[Dict]:
        valid_records: List[Dict] = []
        for record in records:
            try:
                if not record.get("nsu"):
                    raise ValueError("Missing NSU")

                amount_raw = record.get("amount")
                if amount_raw is None:
                    raise ValueError("Missing amount")

                amount = Decimal(str(amount_raw))
                if amount <= 0:
                    raise ValueError("Invalid amount")

                if not record.get("transaction_date"):
                    raise ValueError("Missing transaction date")

                datetime.strptime(record["transaction_date"], "%Y-%m-%d")
                valid_records.append(record)
            except Exception as exc:
                self.logger.warning(
                    "record_validation_failed", record=record, error=str(exc)
                )
        return valid_records

    def _normalize_to_canonical(self, record: Dict) -> Dict:
        amount = Decimal(str(record["amount"]))
        mdr_rate = Decimal("0.023")
        mdr_amount = (amount * mdr_rate).quantize(Decimal("0.01"))
        net_amount = (amount - mdr_amount).quantize(Decimal("0.01"))
        transaction_date = datetime.strptime(
            record["transaction_date"], "%Y-%m-%d"
        ).date()
        brand = self.BRAND_MAPPING.get(record.get("card_brand", "").upper(), "unknown")

        return {
            "nsu": record["nsu"],
            "authorization_code": record.get("authorization_code") or None,
            "amount": str(amount),
            "transaction_date": transaction_date,
            "card_brand": brand,
            "card_last_4": None,
            "mdr_rate": str(mdr_rate),
            "mdr_amount": str(mdr_amount),
            "net_amount": str(net_amount),
            "status": "approved",
        }


__all__ = ["RedeParser"]
