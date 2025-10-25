"""Unit tests for the RedeEEFIParser."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Iterable, Tuple

import pytest

from src.domain.entities import TransactionStatus
from src.infrastructure.acquirers import RedeEEFIParser


def build_fixed_line(length: int, segments: Iterable[Tuple[int, int, str]]) -> str:
    """Helper to craft fixed-width records used in tests."""

    buffer = [" "] * length
    for start, end, value in segments:
        padded = value.ljust(end - start)[: end - start]
        buffer[start:end] = list(padded)
    return "".join(buffer)


def format_decimal(value: Decimal, length: int = 15) -> str:
    quant = (value * Decimal(100)).quantize(Decimal("1"))
    return f"{int(quant):0{length}d}"


@pytest.mark.unit
class TestRedeEEFIParser:
    """Validate parsing rules for Rede EEFI fixed-width files."""

    def test_parse_credit_record(self) -> None:
        parser = RedeEEFIParser()
        header = build_fixed_line(
            140,
            [
                (0, 3, "030"),
                (3, 11, "20012025"),
                (11, 19, "REDE    "),
                (19, 53, "EXTRATO FINANCEIRO"),
                (53, 75, "LOJA TESTE"),
                (75, 81, "000001"),
                (81, 90, "123456789"),
                (90, 105, "DIARIO"),
                (105, 125, "V4.00-05/2023"),
            ],
        )

        credit_line = build_fixed_line(
            160,
            [
                (0, 3, "034"),
                (3, 12, "123456789"),
                (12, 23, "0012345678"),
                (23, 31, "20012025"),
                (31, 46, format_decimal(Decimal("145.00"))),
                (46, 47, "C"),
                (47, 50, "341"),
                (50, 56, "000123"),
                (56, 67, "00012345678"),
                (67, 75, "20012025"),
                (75, 84, "000987654"),
                (84, 92, "19012025"),
                (92, 93, "3"),
                (93, 94, "1"),
                (94, 109, format_decimal(Decimal("150.00"))),
                (109, 124, format_decimal(Decimal("5.00"))),
                (124, 129, "01/01"),
                (129, 131, "00"),
                (131, 140, "123456789"),
            ],
        )

        raw_data = "\n".join([header, credit_line])
        transactions = parser.parse(raw_data, tenant_id="tenant-abc")

        assert len(transactions) == 1
        txn = transactions[0]
        assert txn.nsu.value == "000987654"
        assert txn.transaction_date == date(2025, 1, 20)
        assert txn.amount.amount == Decimal("150.00")
        assert txn.net_amount is not None
        assert txn.net_amount.amount == Decimal("145.00")
        assert txn.mdr_amount is not None
        assert txn.mdr_amount.amount == Decimal("5.00")
        assert txn.status == TransactionStatus.APPROVED
        assert txn.card_brand == "VISA"

    def test_parse_chargeback_record(self) -> None:
        parser = RedeEEFIParser()

        debit_line = build_fixed_line(
            320,
            [
                (0, 3, "038"),
                (3, 12, "123456789"),
                (12, 23, "CHB000001"),
                (23, 31, "21012025"),
                (31, 46, format_decimal(Decimal("40.00"))),
                (46, 47, "D"),
                (47, 50, "341"),
                (50, 56, "000123"),
                (56, 67, "00012345678"),
                (67, 76, "000987654"),
                (76, 84, "20012025"),
                (84, 99, format_decimal(Decimal("150.00"))),
                (99, 103, "16"),
                (103, 131, "CHARGEBACK TESTE"),
                (271, 272, "T"),
                (272, 287, format_decimal(Decimal("40.00"))),
                (287, 302, format_decimal(Decimal("0.00"))),
            ],
        )

        transactions = parser.parse(debit_line, tenant_id="tenant-def")

        assert len(transactions) == 1
        txn = transactions[0]
        assert txn.nsu.value == "000987654"
        assert txn.amount.amount == Decimal("40.00")
        assert txn.net_amount is None
        assert txn.status == TransactionStatus.CHARGEBACK
        assert txn.transaction_date == date(2025, 1, 21)

    def test_invalid_bandeira_collects_error(self) -> None:
        parser = RedeEEFIParser()
        invalid_line = build_fixed_line(
            150,
            [
                (0, 3, "034"),
                (3, 12, "123456789"),
                (12, 23, "0012345678"),
                (23, 31, "20012025"),
                (31, 46, format_decimal(Decimal("100.00"))),
                (46, 47, "C"),
                (47, 50, "341"),
                (50, 56, "000123"),
                (56, 67, "00012345678"),
                (67, 75, "20012025"),
                (75, 84, "000987654"),
                (84, 92, "20012025"),
                (92, 93, "Q"),
                (93, 94, "9"),
                (94, 109, format_decimal(Decimal("110.00"))),
                (109, 124, format_decimal(Decimal("10.00"))),
                (124, 129, "01/01"),
                (129, 131, "00"),
            ],
        )

        transactions = parser.parse(invalid_line, tenant_id="tenant-ghi")

        assert transactions == []
        assert parser.errors
        assert parser.errors[0]["record_type"] == "034"
