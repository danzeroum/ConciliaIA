"""Utilities to build sample Rede EDI content for tests."""

from __future__ import annotations

from typing import Dict

from src.infrastructure.parsers.rede_layouts import get_layout


def _build_record(record_type: str, values: Dict[str, str]) -> str:
    """Build a record line based on layout definition."""
    layout = get_layout(record_type)
    if layout is None:
        raise ValueError(f"Unknown record type: {record_type}")

    max_length = max(end for _, end in layout.fields.values())
    buffer = [" "] * max_length

    for field_name, (start, end) in layout.fields.items():
        if field_name == "record_type":
            value = record_type
        else:
            value = values.get(field_name, "")

        if value is None:
            continue

        str_value = str(value)
        width = end - start
        if len(str_value) > width:
            str_value = str_value[:width]
        else:
            str_value = str_value.ljust(width)

        buffer[start:end] = list(str_value)

    return "".join(buffer)


def sample_rede_edi_content() -> str:
    """Return a representative Rede EEVC EDI content for tests."""
    header = _build_record(
        "00",
        {
            "acquirer_code": "REDECARDS",
            "file_type": "EXTRATO DE MOVIMENTO DE VENDAS",
            "merchant_name": "GRUPO TESTE LTDA",
            "pv": "000123456",
            "file_generation_date": "01012025",
            "file_sequence": "0000001",
            "version": "V3.00 EEVC",
        },
    )

    establishment = _build_record(
        "004",
        {
            "pv": "000123456",
            "merchant_name": "GRUPO TESTE LTDA",
        },
    )

    summary = _build_record(
        "010",
        {
            "pv": "000123456",
            "nsu": "000000001",
            "sale_date": "28122011",
            "installments": "02",
            "gross_amount": "000000000012415",
            "commission_amount": "000000000000585",
            "net_amount": "000000000011830",
        },
    )

    details = _build_record(
        "012",
        {
            "pv": "000123456",
            "nsu": "000000001",
            "sale_date": "28122011",
            "card_number": "************1234",
            "authorization_code": "ABC123",
            "card_brand": "WE",
        },
    )

    detailed = _build_record(
        "024",
        {
            "pv": "000123456",
            "nsu": "000000001",
            "sale_date": "28122011",
            "gross_amount": "000000000012415",
            "card_number": "************1234",
            "authorization_code": "ABC123",
            "card_brand_code": "WE",
        },
    )

    return "\n".join([header, establishment, summary, details, detailed])
