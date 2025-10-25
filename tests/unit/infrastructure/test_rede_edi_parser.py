"""Unit tests for the Rede EDI parser."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Iterable, Tuple

import pytest

from src.infrastructure.acquirers import RedeEDIParser


def build_fixed_line(length: int, segments: Iterable[Tuple[int, int, str]]) -> str:
    """Helper to craft fixed-width records for tests."""

    buffer = [" "] * length
    for start, end, value in segments:
        padded = value.ljust(end - start)[: end - start]
        buffer[start:end] = list(padded)
    return "".join(buffer)


@pytest.mark.unit
class TestRedeEDIParser:
    """Validate parsing logic for Rede positional layouts."""

    def test_parse_eevc_credit_sale(self) -> None:
        parser = RedeEDIParser()
        header = "0020240115EEVC EXTRATO"
        ro_line = build_fixed_line(
            130,
            [
                (0, 3, "010"),
                (3, 12, "000123456"),
                (12, 19, "0000123"),
                (27, 35, "20240115"),
            ],
        )
        cv_line = build_fixed_line(
            150,
            [
                (0, 3, "012"),
                (3, 12, "000123456"),
                (12, 19, "2054920"),
                (19, 27, "20240115"),
                (27, 33, "AB1234"),
                (42, 57, "000000000013000"),
                (57, 60, "001"),
                (60, 63, "003"),
                (63, 67, "0221"),
                (67, 82, "000000000000287"),
                (82, 101, "1234******5678   "),
                (101, 116, "000000000012713"),
            ],
        )
        installment_line = build_fixed_line(
            120,
            [
                (0, 3, "014"),
                (3, 12, "000123456"),
                (12, 19, "2054920"),
                (19, 27, "20240115"),
                (57, 60, "001"),
                (60, 63, "003"),
                (66, 81, "000000000004238"),
            ],
        )

        raw_data = "\n".join([header, ro_line, cv_line, installment_line])
        transactions = parser.parse(raw_data, tenant_id="tenant-123")

        assert len(transactions) == 1
        txn = transactions[0]
        assert txn.nsu.value == "2054920"
        assert txn.transaction_date == date(2024, 1, 15)
        assert txn.card_last_4 == "5678"
        assert txn.net_amount is not None
        assert txn.amount.amount == Decimal("130.00")
        assert txn.net_amount.amount == Decimal("127.13")
        assert txn.mdr_amount is not None
        assert txn.mdr_amount.amount == Decimal("2.87")
        assert txn.mdr_rate is not None
        assert txn.mdr_rate.value == Decimal("0.0221")

    def test_parse_eevd_debit_sale(self) -> None:
        parser = RedeEDIParser()
        header = "0020240116EEVD EXTRATO"
        debit_line = build_fixed_line(
            140,
            [
                (0, 2, "05"),
                (2, 11, "000123456"),
                (14, 23, "987654321"),
                (24, 39, "000000000010000"),
                (39, 42, "ZX1"),
                (42, 50, "20240116"),
                (50, 69, "123456******7890"),
            ],
        )
        raw_data = "\n".join([header, debit_line])
        transactions = parser.parse(raw_data, tenant_id="tenant-456")

        assert len(transactions) == 1
        txn = transactions[0]
        assert txn.nsu.value == "987654321"
        assert txn.amount.amount == Decimal("100.00")
        assert txn.net_amount is None
        assert txn.mdr_amount is None
        assert txn.mdr_rate is None
        assert txn.card_last_4 == "7890"
        assert txn.transaction_date == date(2024, 1, 16)

    def test_parse_eefi_financial_record(self) -> None:
        parser = RedeEDIParser()
        header = "0020240117EEFI FINANCEIRO"
        financial_line = build_fixed_line(
            160,
            [
                (0, 3, "034"),
                (3, 12, "000123456"),
                (12, 24, "FINREF000001"),
                (24, 32, "20240117"),
                (32, 47, "000000000012500"),
                (47, 62, "000000000011500"),
                (62, 77, "000000000001000"),
                (77, 127, "CRÉDITO ANTECIPAÇÃO"),
            ],
        )
        raw_data = "\n".join([header, financial_line])
        transactions = parser.parse(raw_data, tenant_id="tenant-789")

        assert len(transactions) == 1
        txn = transactions[0]
        assert txn.nsu.value.startswith("034")
        assert txn.amount.amount == Decimal("125.00")
        assert txn.net_amount is not None
        assert txn.net_amount.amount == Decimal("115.00")
        assert txn.mdr_amount is not None
        assert txn.mdr_amount.amount == Decimal("10.00")
        assert txn.transaction_date == date(2024, 1, 17)
*** End Patch
