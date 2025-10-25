"""Rede EDI layout definitions for EEVC format."""

from dataclasses import dataclass
from typing import Dict


@dataclass
class RedeRecordLayout:
    """Layout definition for a Rede EDI record type."""

    record_type: str
    name: str
    fields: Dict[str, tuple[int, int]]  # field_name: (start_pos, end_pos)


# Rede EEVC v3.00 Layouts (positions are 0-indexed)
REDE_LAYOUTS = {
    "00": RedeRecordLayout(
        record_type="00",
        name="Header",
        fields={
            "record_type": (0, 2),
            "acquirer_code": (2, 11),
            "file_type": (11, 45),
            "merchant_name": (45, 67),
            "pv": (67, 76),
            "file_generation_date": (76, 84),
            "file_sequence": (84, 91),
            "version": (91, 112),
        },
    ),
    "004": RedeRecordLayout(
        record_type="004",
        name="Estabelecimento",
        fields={
            "record_type": (0, 3),
            "pv": (3, 12),
            "merchant_name": (12, 34),
        },
    ),
    "010": RedeRecordLayout(
        record_type="010",
        name="Resumo de Venda (CV)",
        fields={
            "record_type": (0, 3),
            "pv": (3, 12),
            "nsu": (12, 21),
            "sale_date": (21, 29),  # DDMMYYYY
            "installments": (29, 31),
            "gross_amount": (46, 61),  # centavos
            "commission_amount": (61, 76),  # centavos
            "net_amount": (76, 91),  # centavos
        },
    ),
    "012": RedeRecordLayout(
        record_type="012",
        name="Detalhes de Venda (CV)",
        fields={
            "record_type": (0, 3),
            "pv": (3, 12),
            "nsu": (12, 21),
            "sale_date": (21, 29),
            "card_number": (60, 79),  # masked
            "authorization_code": (79, 85),
            "card_brand": (175, 177),  # ID/WE/etc
        },
    ),
    "024": RedeRecordLayout(
        record_type="024",
        name="Transação Detalhada",
        fields={
            "record_type": (0, 3),
            "pv": (3, 12),
            "nsu": (12, 21),
            "sale_date": (21, 29),
            "gross_amount": (29, 44),
            "card_number": (60, 79),
            "authorization_code": (79, 85),
            "card_brand_code": (175, 177),
        },
    ),
}


def get_layout(record_type: str) -> RedeRecordLayout | None:
    """Get layout definition for a record type."""
    return REDE_LAYOUTS.get(record_type)


def extract_field(line: str, field_name: str, layout: RedeRecordLayout) -> str:
    """Extract a field value from a line using layout definition."""
    if field_name not in layout.fields:
        return ""

    start, end = layout.fields[field_name]
    try:
        return line[start:end].strip()
    except IndexError:
        return ""


CARD_BRAND_MAP = {
    "ID": "VISA",
    "WE": "MASTERCARD",
    "WH": "MASTERCARD",
    "EL": "ELO",
    "MC": "MASTERCARD",
    "AM": "AMEX",
    "HI": "HIPERCARD",
}


def map_card_brand(brand_code: str) -> str:
    """Map Rede card brand code to standard name."""
    return CARD_BRAND_MAP.get(brand_code.upper(), "UNKNOWN")
