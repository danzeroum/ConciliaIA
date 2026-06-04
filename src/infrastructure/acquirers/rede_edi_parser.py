"""Rede EDI fixed-width file parser."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, Iterable, List, Mapping, MutableMapping, Optional

from src.domain.value_objects import Acquirer

from .base_parser import AcquirerParserError, BaseAcquirerParser


@dataclass(frozen=True)
class FieldSpec:
    """Description of a fixed-width field."""

    start: int
    end: int
    kind: str = "str"
    precision: int = 2


class RedeEDIParser(BaseAcquirerParser):
    """Parse Rede EDI files (EEVC, EEVD, EEFI, EESA)."""

    EEVC_LAYOUTS: Mapping[str, Mapping[str, FieldSpec]] = {
        "010": {
            "record_type": FieldSpec(0, 3),
            "establishment": FieldSpec(3, 12),
            "ro_number": FieldSpec(12, 19),
            "sale_date": FieldSpec(27, 35, "date"),
        },
        "012": {
            "record_type": FieldSpec(0, 3),
            "establishment": FieldSpec(3, 12),
            "nsu": FieldSpec(12, 19),
            "transaction_date": FieldSpec(19, 27, "date"),
            "authorization_code": FieldSpec(27, 33),
            "gross_amount": FieldSpec(42, 57, "decimal", 2),
            "installment_number": FieldSpec(57, 60, "int"),
            "installment_total": FieldSpec(60, 63, "int"),
            "mdr_rate": FieldSpec(63, 67, "percent", 4),
            "mdr_amount": FieldSpec(67, 82, "decimal", 2),
            "card_masked": FieldSpec(82, 101),
            "net_amount": FieldSpec(101, 116, "decimal", 2),
        },
        "014": {
            "record_type": FieldSpec(0, 3),
            "establishment": FieldSpec(3, 12),
            "nsu": FieldSpec(12, 19),
            "transaction_date": FieldSpec(19, 27, "date"),
            "installment_number": FieldSpec(57, 60, "int"),
            "installment_total": FieldSpec(60, 63, "int"),
            "installment_amount": FieldSpec(66, 81, "decimal", 2),
        },
    }

    EEVD_LAYOUTS: Mapping[str, Mapping[str, FieldSpec]] = {
        "05": {
            "record_type": FieldSpec(0, 2),
            "establishment": FieldSpec(2, 11),
            "nsu": FieldSpec(14, 23),
            "gross_amount": FieldSpec(24, 39, "decimal", 2),
            "authorization_code": FieldSpec(39, 42),
            "transaction_date": FieldSpec(42, 50, "date"),
            "card_masked": FieldSpec(50, 69),
        }
    }

    EEFI_LAYOUTS: Mapping[str, Mapping[str, FieldSpec]] = {
        record_type: {
            "record_type": FieldSpec(0, 3),
            "establishment": FieldSpec(3, 12),
            # EEFI records carry a financial reference (not a transaction NSU)
            # at 12-24; the NSU is synthesized per record type in _parse_eefi.
            "transaction_date": FieldSpec(24, 32, "date"),
            "gross_amount": FieldSpec(32, 47, "decimal", 2),
            "net_amount": FieldSpec(47, 62, "decimal", 2),
            "mdr_amount": FieldSpec(62, 77, "decimal", 2),
            "description": FieldSpec(77, 127),
        }
        for record_type in ("034", "035", "036", "037", "038", "039", "040", "041", "042", "043", "044", "045", "046", "047", "048", "049", "050")
    }

    EESA_LAYOUT: Mapping[str, FieldSpec] = {
        "record_type": FieldSpec(0, 3),
        "establishment": FieldSpec(3, 12),
        "nsu": FieldSpec(12, 24),
        "transaction_date": FieldSpec(24, 32, "date"),
        "gross_amount": FieldSpec(32, 47, "decimal", 2),
        "net_amount": FieldSpec(47, 62, "decimal", 2),
        "description": FieldSpec(62, 112),
    }

    def __init__(self) -> None:
        super().__init__(Acquirer.REDE)

    def _parse_raw_data(self, raw_data: str | bytes | Dict | List[Dict]) -> List[Dict]:
        if isinstance(raw_data, list):
            return raw_data
        if isinstance(raw_data, dict):
            return [raw_data]
        if isinstance(raw_data, bytes):
            raw_text = raw_data.decode("latin-1")
        else:
            raw_text = raw_data
        lines = [line for line in raw_text.splitlines() if line.strip()]
        if not lines:
            return []
        header = lines[0]
        if "EEVC" in header:
            return self._parse_eevc(lines)
        if "EEVD" in header:
            return self._parse_eevd(lines)
        if "EEFI" in header:
            return self._parse_eefi(lines)
        if "EESA" in header:
            return self._parse_eesa(lines)
        raise AcquirerParserError(f"Tipo arquivo Rede desconhecido: {header[:20]}")

    def _parse_eevc(self, lines: Iterable[str]) -> List[Dict]:
        records: List[Dict] = []
        current_ro: Optional[Dict] = None
        for line in lines:
            record_type = line[:3]
            if record_type == "010":
                current_ro = self._extract_fields(line, self.EEVC_LAYOUTS["010"])
            elif record_type == "012":
                cv = self._extract_fields(line, self.EEVC_LAYOUTS["012"])
                if current_ro:
                    cv["ro_number"] = current_ro.get("ro_number")
                card_masked = cv.get("card_masked")
                if card_masked:
                    digits = "".join(ch for ch in card_masked if ch.isdigit())
                    cv["card_last_4"] = digits[-4:] if len(digits) >= 4 else None
                if cv.get("installment_total", 1) and cv.get("installment_total", 1) > 1:
                    cv["installments"] = []
                records.append(cv)
            elif record_type == "014" and records:
                parcel = self._extract_fields(line, self.EEVC_LAYOUTS["014"])
                if "installments" in records[-1]:
                    records[-1]["installments"].append(parcel)
        return records

    def _parse_eevd(self, lines: Iterable[str]) -> List[Dict]:
        records: List[Dict] = []
        for line in lines:
            if not line:
                continue
            record_type = line[:2]
            if record_type == "05":
                cv = self._extract_fields(line, self.EEVD_LAYOUTS["05"])
                card_masked = cv.get("card_masked")
                if card_masked:
                    digits = "".join(ch for ch in card_masked if ch.isdigit())
                    cv["card_last_4"] = digits[-4:] if len(digits) >= 4 else None
                records.append(cv)
        return records

    def _parse_eefi(self, lines: Iterable[str]) -> List[Dict]:
        records: List[Dict] = []
        counters: Dict[str, int] = {}
        for line in lines:
            record_type = line[:3]
            if record_type in self.EEFI_LAYOUTS:
                entry = self._extract_fields(line, self.EEFI_LAYOUTS[record_type])
                counters.setdefault(record_type, 0)
                counters[record_type] += 1
                entry.setdefault("nsu", f"{record_type}{counters[record_type]:06d}")
                entry.setdefault("status", "settled")
                records.append(entry)
        return records

    def _parse_eesa(self, lines: Iterable[str]) -> List[Dict]:
        records: List[Dict] = []
        counter = 0
        for line in lines:
            record_type = line[:3]
            if record_type == "012":
                entry = self._extract_fields(line, self.EEVC_LAYOUTS["012"])
                counter += 1
                entry.setdefault("nsu", f"EESA{counter:06d}")
                records.append(entry)
            elif record_type == "014" and records:
                parcel = self._extract_fields(line, self.EEVC_LAYOUTS["014"])
                if "installments" in records[-1]:
                    records[-1]["installments"].append(parcel)
        if not records:
            for line in lines:
                if line[:3] == "001":
                    base = self._extract_fields(line, self.EESA_LAYOUT)
                    counter += 1
                    base.setdefault("nsu", f"EESA{counter:06d}")
                    records.append(base)
        return records

    def _extract_fields(self, line: str, layout: Mapping[str, FieldSpec]) -> Dict:
        parsed: Dict[str, object] = {}
        for field_name, spec in layout.items():
            raw_value = line[spec.start : spec.end]
            value = self._convert_field(raw_value, spec)
            if value is not None:
                parsed[field_name] = value
        return parsed

    def _convert_field(self, raw: str, spec: FieldSpec) -> Optional[object]:
        text = raw.rstrip()
        if spec.kind == "str":
            return text.strip() or None
        text = text.strip()
        if not text:
            return None
        if spec.kind == "int":
            return int(text)
        if spec.kind == "decimal":
            return self._to_decimal(text, spec.precision)
        if spec.kind == "percent":
            return self._to_decimal(text, spec.precision)
        if spec.kind == "date":
            return self._parse_date(text)
        return text or None

    def _to_decimal(self, value: str, precision: int) -> Optional[Decimal]:
        sign = 1
        stripped = value.strip()
        if not stripped:
            return None
        if stripped.startswith("-"):
            sign = -1
            stripped = stripped[1:]
        elif stripped.endswith("-"):
            sign = -1
            stripped = stripped[:-1]
        digits = "".join(ch for ch in stripped if ch.isdigit())
        if not digits:
            return None
        quant = Decimal(sign) * Decimal(digits) / (Decimal(10) ** precision)
        return quant.quantize(Decimal("1." + ("0" * precision)), rounding=ROUND_HALF_UP)

    def _parse_date(self, value: str) -> Optional[date]:
        for fmt in ("%Y%m%d", "%d%m%Y"):
            try:
                return datetime.strptime(value, fmt).date()
            except ValueError:
                continue
        return None

    def _validate_data(self, records: List[Dict]) -> List[Dict]:
        valid: List[Dict] = []
        for record in records:
            if not record.get("nsu"):
                continue
            if not record.get("gross_amount"):
                continue
            transaction_date = record.get("transaction_date") or record.get(
                "sale_date"
            )
            if transaction_date and isinstance(transaction_date, date):
                record["transaction_date"] = transaction_date
                valid.append(record)
        return valid

    def _normalize_to_canonical(self, record: Dict) -> Dict:
        gross_amount: Decimal = record["gross_amount"]
        net_amount: Optional[Decimal] = record.get("net_amount")
        mdr_amount: Optional[Decimal] = record.get("mdr_amount")
        if net_amount is None and mdr_amount is not None:
            net_amount = (gross_amount - mdr_amount).quantize(Decimal("0.01"))
        if mdr_amount is None and net_amount is not None:
            mdr_amount = (gross_amount - net_amount).quantize(Decimal("0.01"))
        mdr_rate: Optional[Decimal] = record.get("mdr_rate")
        if mdr_rate is None and mdr_amount is not None and gross_amount:
            if gross_amount != 0:
                mdr_rate = (mdr_amount / gross_amount).quantize(Decimal("0.0001"))
        transaction_date: date = record["transaction_date"]

        # The authorization code is optional; a malformed value (outside the
        # domain's 4-10 char rule) must not drop the whole transaction.
        auth_code = record.get("authorization_code")
        if isinstance(auth_code, str):
            auth_code = auth_code.strip() or None
            if auth_code is not None and not (4 <= len(auth_code) <= 10):
                auth_code = None

        canonical: MutableMapping[str, object] = {
            "nsu": str(record["nsu"]),
            "authorization_code": auth_code,
            "amount": str(gross_amount.quantize(Decimal("0.01"))),
            "transaction_date": transaction_date,
            "card_brand": record.get("card_brand", "unknown"),
            "card_last_4": record.get("card_last_4"),
            "mdr_rate": str(mdr_rate) if mdr_rate is not None else None,
            "mdr_amount": str(mdr_amount.quantize(Decimal("0.01")))
            if mdr_amount is not None
            else None,
            "net_amount": str(net_amount.quantize(Decimal("0.01")))
            if net_amount is not None
            else None,
            "status": record.get("status", "approved"),
        }
        return dict(canonical)


__all__ = ["RedeEDIParser"]
