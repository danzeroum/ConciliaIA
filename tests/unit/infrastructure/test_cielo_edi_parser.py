"""Unit tests for the Cielo EDI parser."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from src.infrastructure.acquirers import CieloEDIParser


@pytest.mark.unit
class TestCieloEDIParser:
    """Validate parsing of Cielo fixed-width files."""

    def test_parse_detail_record(self) -> None:
        parser = CieloEDIParser()
        today = date.today().strftime("%Y%m%d")
        line = (
            "3"
            "1234567890"
            "0001234"
            "123456789"
            "ABC123"
            f"{today}"
            f"{today}"
            "0000000010000"
            "+"
            "01"
            "01"
            "0250"
            "0000000000250"
            "0000000009750"
            "************1234"
            "001"
            "1"
        )
        padded = line + ("0" * max(0, 120 - len(line)))
        record = parser._parse_raw_data(padded)[0]
        assert record["nsu"] == "123456789"
        assert record["authorization_code"] == "ABC123"
        assert record["gross_amount"] == "0000000010000"

    def test_normalize_cielo_record(self) -> None:
        parser = CieloEDIParser()
        today = date.today().strftime("%Y%m%d")
        record = {
            "nsu": "123456789",
            "authorization_code": "ABC123",
            "gross_amount": "0000000010000",
            "sign_gross": "+",
            "commission_rate": "0250",
            "commission_amount": "0000000000250",
            "net_amount": "0000000009750",
            "transaction_date": today,
            "card_number": "************1234",
            "product_code": "001",
        }
        canonical = parser._normalize_to_canonical(record)
        assert canonical["nsu"] == "123456789"
        assert Decimal(canonical["amount"]) == Decimal("100.00")
        assert Decimal(canonical["mdr_rate"]) == Decimal("0.0250")
        assert Decimal(canonical["mdr_amount"]) == Decimal("2.50")
        assert Decimal(canonical["net_amount"]) == Decimal("97.50")
        assert canonical["card_brand"] == "visa"
        assert canonical["card_last_4"] == "1234"

    def test_parse_full_edi_file(self) -> None:
        parser = CieloEDIParser()
        today = date.today().strftime("%Y%m%d")
        line_template = (
            "3"
            "1234567890"
            "0001234"
            "{nsu}"
            "ABC123"
            f"{today}"
            f"{today}"
            "0000000010000"
            "+"
            "01"
            "01"
            "0250"
            "0000000000250"
            "0000000009750"
            "************1234"
            "001"
            "1"
        )
        line_one = line_template.format(nsu="123456789")
        line_two = line_template.format(nsu="987654321")

        def pad(value: str) -> str:
            return value + ("0" * max(0, 120 - len(value)))

        edi_content = "\n".join([pad(line_one), pad(line_two)])
        transactions = parser.parse(edi_content, tenant_id="tenant-123")
        assert len(transactions) == 2
        assert transactions[0].nsu.value == "123456789"
        assert transactions[1].nsu.value == "987654321"
