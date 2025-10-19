"""Cielo EDI parser for fixed-width positional files."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Dict, List

from src.domain.value_objects import Acquirer

from .base_parser import BaseAcquirerParser


class CieloEDIParser(BaseAcquirerParser):
    """Parse Cielo EDI files (Extrato Eletrônico)."""

    DETAIL_LAYOUT = {
        "record_type": (0, 1),
        "establishment_code": (1, 11),
        "ro_number": (11, 18),
        "nsu": (18, 27),
        "authorization_code": (27, 33),
        "transaction_date": (33, 41),
        "sale_date": (41, 49),
        "gross_amount": (49, 62),
        "sign_gross": (62, 63),
        "installment_current": (63, 65),
        "installment_total": (65, 67),
        "commission_rate": (67, 71),
        "commission_amount": (71, 84),
        "net_amount": (84, 97),
        "card_number": (97, 116),
        "product_code": (116, 119),
        "transaction_type": (119, 120),
    }

    BRAND_MAPPING = {
        "001": "visa",
        "002": "mastercard",
        "003": "amex",
        "004": "elo",
        "005": "diners",
        "006": "hipercard",
    }

    def __init__(self) -> None:
        super().__init__(Acquirer.CIELO)

    def _parse_raw_data(self, raw_data: str | bytes) -> List[Dict]:
        if isinstance(raw_data, bytes):
            raw_data = raw_data.decode("latin-1")

        records: List[Dict] = []
        for line_number, line in enumerate(raw_data.strip().splitlines(), start=1):
            if not line or len(line) < 120:
                continue

            record_type = line[0:1]
            if record_type != "3":
                continue

            try:
                record = {}
                for field, (start, end) in self.DETAIL_LAYOUT.items():
                    record[field] = line[start:end].strip()
                record["_line_number"] = line_number
                records.append(record)
            except Exception as exc:  # pragma: no cover - defensive logging
                self.logger.warning(
                    "line_parse_failed", line_number=line_number, error=str(exc)
                )
        return records

    def _validate_data(self, records: List[Dict]) -> List[Dict]:
        valid_records: List[Dict] = []
        for record in records:
            try:
                if not record.get("nsu"):
                    raise ValueError("Missing NSU")

                if not record.get("gross_amount"):
                    raise ValueError("Missing gross amount")

                if not record.get("transaction_date"):
                    raise ValueError("Missing transaction date")

                gross = Decimal(record["gross_amount"]) / Decimal("100")
                if record.get("sign_gross") == "-":
                    gross = -gross
                if gross <= 0:
                    raise ValueError("Gross amount must be positive")

                datetime.strptime(record["transaction_date"], "%Y%m%d")
                valid_records.append(record)
            except Exception as exc:
                self.logger.warning(
                    "record_validation_failed", record=record, error=str(exc)
                )
        return valid_records

    def _normalize_to_canonical(self, record: Dict) -> Dict:
        gross_amount = Decimal(record["gross_amount"]) / Decimal("100")
        if record.get("sign_gross") == "-":
            gross_amount = abs(gross_amount)

        commission_amount = (
            Decimal(record.get("commission_amount") or "0") / Decimal("100")
        )
        net_amount = Decimal(record.get("net_amount") or "0") / Decimal("100")

        commission_rate_raw = record.get("commission_rate") or "0"
        mdr_rate = (Decimal(commission_rate_raw) / Decimal("10000")) if commission_rate_raw else Decimal("0")

        transaction_date = datetime.strptime(record["transaction_date"], "%Y%m%d").date()
        card_number = record.get("card_number", "")
        card_last_4 = card_number[-4:] if len(card_number) >= 4 else None
        brand = self.BRAND_MAPPING.get(record.get("product_code", ""), "unknown")

        return {
            "nsu": record["nsu"],
            "authorization_code": record.get("authorization_code") or None,
            "amount": str(gross_amount),
            "transaction_date": transaction_date,
            "card_brand": brand,
            "card_last_4": card_last_4,
            "mdr_rate": str(mdr_rate),
            "mdr_amount": str(commission_amount),
            "net_amount": str(net_amount),
            "status": "approved",
        }


__all__ = ["CieloEDIParser"]
