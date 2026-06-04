"""Unit tests for Rede EDI parser."""

from decimal import Decimal
from datetime import date

import pytest

from src.infrastructure.parsers.rede_edi_parser import RedeEDIParser
from src.domain.value_objects import Acquirer
from tests.utils.rede_edi_sample import sample_rede_edi_content


class TestRedeEDIParser:
    """Test suite for RedeEDIParser."""

    @pytest.fixture
    def parser(self) -> RedeEDIParser:
        """Create parser instance."""
        return RedeEDIParser()

    @pytest.fixture
    def valid_edi_content(self) -> str:
        """Sample valid Rede EDI content."""
        return sample_rede_edi_content()

    @pytest.fixture
    def invalid_edi_content(self) -> str:
        """Sample invalid EDI content."""
        return "This is not a valid EDI file"

    def test_validate_valid_file(self, parser: RedeEDIParser, valid_edi_content: str):
        """Test validation of valid EDI file."""
        assert parser.validate(valid_edi_content) is True

    def test_validate_invalid_file(self, parser: RedeEDIParser, invalid_edi_content: str):
        """Test validation of invalid EDI file."""
        assert parser.validate(invalid_edi_content) is False

    def test_validate_empty_file(self, parser: RedeEDIParser):
        """Test validation of empty file."""
        assert parser.validate("") is False
        assert parser.validate("   ") is False

    def test_parse_valid_file(self, parser: RedeEDIParser, valid_edi_content: str):
        """Test parsing of valid EDI file."""
        tenant_id = "test-tenant-123"
        transactions = parser.parse(valid_edi_content, tenant_id)

        assert len(transactions) > 0

        # Verify first transaction
        txn = transactions[0]
        assert txn.tenant_id == tenant_id
        assert txn.acquirer == Acquirer.REDE
        assert txn.nsu.value == "000000001"
        assert txn.amount.amount == Decimal("124.15")
        assert txn.transaction_date == date(2011, 12, 28)
        assert txn.installments == 2

    def test_parse_invalid_file_raises_error(self, parser: RedeEDIParser, invalid_edi_content: str):
        """Test that parsing invalid file raises ValueError."""
        with pytest.raises(ValueError, match="Invalid Rede EDI file format"):
            parser.parse(invalid_edi_content, "test-tenant")

    def test_parse_date_ddmmyyyy(self, parser: RedeEDIParser):
        """Test date parsing in DDMMYYYY format."""
        result = parser.parse_date("28122011", "DDMMYYYY")
        assert result == "2011-12-28"

    def test_parse_date_invalid_format(self, parser: RedeEDIParser):
        """Test date parsing with invalid format returns fallback."""
        result = parser.parse_date("invalid", "DDMMYYYY")
        assert result  # Should return some valid date (fallback)

    def test_parse_amount_cents(self, parser: RedeEDIParser):
        """Test amount parsing from cents."""
        result = parser.parse_amount("12415", is_cents=True)
        assert result == 124.15

    def test_parse_amount_reais(self, parser: RedeEDIParser):
        """Test amount parsing from reais."""
        result = parser.parse_amount("124.15", is_cents=False)
        assert result == 124.15

    def test_parse_amount_invalid(self, parser: RedeEDIParser):
        """Test amount parsing with invalid input."""
        result = parser.parse_amount("invalid", is_cents=True)
        assert result == 0.0

    def test_parse_multiple_transactions(self, parser: RedeEDIParser, valid_edi_content: str):
        """Test parsing file with multiple transactions."""
        transactions = parser.parse(valid_edi_content, "test-tenant")

        # Should extract at least 1 transaction from sample
        assert len(transactions) >= 1

        # All transactions should have required fields
        for txn in transactions:
            assert txn.tenant_id == "test-tenant"
            assert txn.acquirer == Acquirer.REDE
            assert txn.nsu.value
            assert txn.amount.amount > 0
            assert isinstance(txn.transaction_date, date)

    def test_parse_transaction_with_installments(
        self, parser: RedeEDIParser, valid_edi_content: str
    ):
        """Test parsing transaction with installments."""
        transactions = parser.parse(valid_edi_content, "test-tenant")

        # Find transaction with installments
        installment_txn = next((t for t in transactions if t.installments > 1), None)

        assert installment_txn is not None
        assert installment_txn.installments >= 2

    def test_parse_calculates_net_amount(self, parser: RedeEDIParser, valid_edi_content: str):
        """Test that net amount is calculated from gross - commission."""
        transactions = parser.parse(valid_edi_content, "test-tenant")

        for txn in transactions:
            if txn.mdr_amount:
                expected_net = txn.amount.amount - txn.mdr_amount.amount
                assert abs(txn.net_amount.amount - expected_net) < Decimal("0.01")
