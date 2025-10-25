"""Unit tests for the Rede TORC parser."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from src.infrastructure.acquirers.rede_torc_parser import (
    RedeTORCParser,
    TORCValidationError,
)


@pytest.fixture
def parser() -> RedeTORCParser:
    return RedeTORCParser()


def test_parse_header_valid(parser: RedeTORCParser) -> None:
    line = (
        "00,123456789,18012025,18012025,Movimentação diária – Cartões de Débito,"
        "Rede,Loja Teste,0001,diário,V2.00 - 05/2023 EEVD"
    )
    header = parser._parse_header(line)

    assert header["sequencia"] == "0001"
    assert header["record_type"] == "00"


def test_reject_invalid_sequence(parser: RedeTORCParser) -> None:
    content = "\n".join(
        [
            "00,123456789,18012025,18012025,Mov Diária,Rede,Loja,0002,diário,V2.00",
            "01,123456789,19012025,18012025,987654321,5,15000,150,14850,D,001,0123,12345678901,1",
            "04,0000000000000000000000000000000000000000000000000000000000000003,3",
        ]
    )

    with pytest.raises(TORCValidationError):
        parser.parse(content, tenant_id="tenant-test")


def test_parse_resumo_debito(parser: RedeTORCParser) -> None:
    line = (
        "01,123456789,19012025,18012025,987654321,5,15000,150,14850,D,001,0123,12345678901,1"
    )
    resumo = parser._parse_resumo_vendas(line)

    assert resumo["gross_amount"] == Decimal("150.00")
    assert resumo["net_amount"] == Decimal("148.50")
    assert resumo["summary_type"] == "D"


def test_parse_compre_saque(parser: RedeTORCParser) -> None:
    line_resumo = (
        "01,123456789,19012025,18012025,111222333,1,10000,100,9900,D,001,0123,12345678901,1"
    )
    line_detalhe = (
        "05,123456789,111222333,18012025,10000,100,9900,1234567890123456,V,123456789012,"
        "19012025,01,143000,12345678,02,986,7000,3000,1,ABC123,001"
    )

    resumo = parser._parse_resumo_vendas(line_resumo)
    detalhe = parser._parse_detalhe_cv(line_detalhe)

    assert resumo["gross_amount"] == Decimal("100.00")
    assert detalhe["compre_saque"]["valor_compra"] == Decimal("70.00")
    assert detalhe["compre_saque"]["valor_saque"] == Decimal("30.00")


def test_validate_total_registros(parser: RedeTORCParser) -> None:
    records = [
        {
            "record_type": "00",
            "sequencia": "0001",
            "processamento": "diário",
        },
        {
            "record_type": "01",
            "nsu": "1",
            "card_brand": "maestro",
            "gross_amount": Decimal("10.00"),
            "discount_amount": Decimal("1.00"),
            "net_amount": Decimal("9.00"),
            "transaction_date": date(2025, 1, 18),
        },
        {"record_type": "04", "total_registros": "3"},
    ]

    validated = parser._validate_data(records)

    assert len(validated) == 1
