"""Integration tests for the Cielo EDI client."""

from __future__ import annotations

import os
from datetime import date
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.infrastructure.acquirers.cielo_client import CieloEDIClient


class _AsyncContextManager:
    """Utility context manager that yields a predefined value."""

    def __init__(self, value: object) -> None:
        self._value = value

    async def __aenter__(self) -> object:
        return self._value

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: object | None,
    ) -> bool:
        return False


@pytest.mark.integration
class TestCieloIntegration:
    """Integration tests para Cielo EDI."""

    @pytest.fixture
    def cielo_client(self) -> CieloEDIClient:
        os.environ.setdefault("CIELO_SFTP_HOST", "sftp.cielo.com.br")
        os.environ.setdefault("CIELO_SFTP_PORT", "22")
        os.environ.setdefault("CIELO_SFTP_USER", "test_user")
        os.environ.setdefault("CIELO_SFTP_PASSWORD", "test_pass")
        os.environ.setdefault("CIELO_EC_NUMBER", "1234567890")
        os.environ.setdefault("CIELO_API_HOST", "https://api.cielo.com.br")
        return CieloEDIClient()

    @pytest.fixture
    def sample_edi_content(self) -> str:
        def detail_line(
            ro_number: int,
            nsu: str,
            authorization: str,
            gross_cents: int,
            commission_cents: int,
            net_cents: int,
            card_number: str,
            product_code: str,
        ) -> str:
            return (
                "3"
                + f"{1234567890:0>10}"
                + f"{ro_number:0>7}"
                + f"{nsu:0>9}"
                + f"{authorization:<6}"[:6]
                + "20250115"
                + "20250215"
                + f"{gross_cents:0>13}"
                + "+"
                + "01"
                + "01"
                + "0150"
                + f"{commission_cents:0>13}"
                + f"{net_cents:0>13}"
                + f"{card_number:<19}"[:19]
                + f"{product_code:<3}"[:3]
                + "1"
            )

        lines = [
            "0CIELO     EXTRATO EDI          20250115".ljust(200),
            detail_line(
                ro_number=1,
                nsu="123456789",
                authorization="ABC123",
                gross_cents=15000,
                commission_cents=450,
                net_cents=14550,
                card_number="1234567890123456789",
                product_code="001",
            ),
            detail_line(
                ro_number=2,
                nsu="987654321",
                authorization="XYZ789",
                gross_cents=20000,
                commission_cents=600,
                net_cents=19400,
                card_number="9876543210987654321",
                product_code="002",
            ),
            "9CIELO     000000002".ljust(200),
        ]
        return "\n".join(lines)

    @pytest.mark.asyncio
    async def test_parse_edi_success(
        self, cielo_client: CieloEDIClient, sample_edi_content: str
    ) -> None:
        transactions = cielo_client.parse_edi(
            edi_content=sample_edi_content,
            tenant_id="tenant-123",
        )

        assert len(transactions) == 2

        txn1 = transactions[0]
        assert txn1.tenant_id == "tenant-123"
        assert txn1.acquirer == "cielo"
        assert txn1.nsu.value == "123456789"
        assert txn1.amount.amount == Decimal("150.00")
        assert txn1.mdr_amount is not None
        assert txn1.mdr_amount.amount == Decimal("4.50")
        assert txn1.net_amount.amount == Decimal("145.50")
        assert txn1.transaction_date == date(2025, 1, 15)
        assert txn1.card_last_4 == "6789"

        txn2 = transactions[1]
        assert txn2.nsu.value == "987654321"
        assert txn2.amount.amount == Decimal("200.00")

    @pytest.mark.asyncio
    async def test_fetch_transactions_e2e(
        self,
        cielo_client: CieloEDIClient,
        sample_edi_content: str,
    ) -> None:
        with patch(
            "src.infrastructure.acquirers.cielo_edi_client.aiohttp.ClientSession"
        ) as mock_session:
            mock_auth_response = AsyncMock()
            mock_auth_response.status = 200
            mock_auth_response.json.return_value = {"access_token": "fake-token-123"}

            mock_edi_response = AsyncMock()
            mock_edi_response.status = 200
            mock_edi_response.text.return_value = sample_edi_content

            session_mock = MagicMock()
            session_mock.post.return_value = _AsyncContextManager(mock_auth_response)
            session_mock.get.return_value = _AsyncContextManager(mock_edi_response)

            session_context = AsyncMock()
            session_context.__aenter__.return_value = session_mock
            mock_session.return_value = session_context

            transactions = await cielo_client.fetch_transactions(
                tenant_id="tenant-123",
                start_date=date(2025, 1, 1),
                end_date=date(2025, 1, 31),
            )

            assert len(transactions) == 2
            assert all(t.acquirer == "cielo" for t in transactions)

    @pytest.mark.asyncio
    async def test_handle_authentication_failure(self, cielo_client: CieloEDIClient) -> None:
        with patch(
            "src.infrastructure.acquirers.cielo_edi_client.aiohttp.ClientSession"
        ) as mock_session:
            mock_auth_response = AsyncMock()
            mock_auth_response.status = 401
            mock_auth_response.text.return_value = "Invalid credentials"

            session_mock = MagicMock()
            session_mock.post.return_value = _AsyncContextManager(mock_auth_response)

            session_context = AsyncMock()
            session_context.__aenter__.return_value = session_mock
            mock_session.return_value = session_context

            with pytest.raises(RuntimeError) as exc_info:
                await cielo_client.fetch_transactions(
                    tenant_id="tenant-123",
                    start_date=date(2025, 1, 1),
                    end_date=date(2025, 1, 31),
                )

            assert "Cielo authentication failed: 401" in str(exc_info.value)
