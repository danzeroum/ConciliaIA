"""Integration tests for the Cielo EDI client."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from unittest.mock import AsyncMock, patch

import pytest

from src.infrastructure.acquirers.cielo_client import CieloEDIClient
from src.infrastructure.security import SecretsManager


@pytest.mark.integration
class TestCieloIntegration:
    """Integration tests para Cielo EDI."""

    @pytest.fixture
    def mock_secrets_manager(self) -> AsyncMock:
        secrets = AsyncMock(spec=SecretsManager)
        secrets.get_acquirer_credentials.return_value = {
            "merchant_id": "MERCHANT123",
            "api_key": "fake-api-key-for-testing",
        }
        return secrets

    @pytest.fixture
    def cielo_client(self, mock_secrets_manager: AsyncMock) -> CieloEDIClient:
        return CieloEDIClient(secrets_manager=mock_secrets_manager)

    @pytest.fixture
    def sample_edi_content(self) -> str:
        return (
            "0CIELO     EXTRATO EDI          20250115" + " " * 180
            + "\n312345678900000001234567890000001502025011520250215000000000015000000000000045000000000014550001"
            + " " * 150
            + "\n312345678900000002345678900000002002025011520250215000000000020000000000000060000000000019400001"
            + " " * 150
            + "\n9CIELO     000000002" + " " * 200
        )

    @pytest.mark.asyncio
    async def test_parse_edi_success(
        self, cielo_client: CieloEDIClient, sample_edi_content: str
    ) -> None:
        transactions = cielo_client._parse_edi(
            edi_content=sample_edi_content,
            tenant_id="tenant-123",
        )

        assert len(transactions) == 2

        txn1 = transactions[0]
        assert txn1.tenant_id == "tenant-123"
        assert txn1.acquirer == "cielo"
        assert txn1.nsu == "1234567890000"
        assert txn1.gross_amount.amount == Decimal("150.00")
        assert txn1.mdr_fee.amount == Decimal("4.50")
        assert txn1.net_amount.amount == Decimal("145.50")
        assert txn1.transaction_date == date(2025, 1, 15)
        assert txn1.settlement_date == date(2025, 2, 15)

        txn2 = transactions[1]
        assert txn2.nsu == "2345678900000"
        assert txn2.gross_amount.amount == Decimal("200.00")

    @pytest.mark.asyncio
    async def test_fetch_transactions_e2e(
        self,
        cielo_client: CieloEDIClient,
        sample_edi_content: str,
    ) -> None:
        with patch("aiohttp.ClientSession") as mock_session:
            mock_auth_response = AsyncMock()
            mock_auth_response.status = 200
            mock_auth_response.json.return_value = {"access_token": "fake-token-123"}

            mock_edi_response = AsyncMock()
            mock_edi_response.status = 200
            mock_edi_response.text.return_value = sample_edi_content

            mock_context = AsyncMock()
            mock_context.__aenter__.return_value.post.return_value.__aenter__.return_value = (
                mock_auth_response
            )
            mock_context.__aenter__.return_value.get.return_value.__aenter__.return_value = (
                mock_edi_response
            )
            mock_session.return_value = mock_context

            transactions = await cielo_client.fetch_transactions(
                tenant_id="tenant-123",
                start_date=date(2025, 1, 1),
                end_date=date(2025, 1, 31),
            )

            assert len(transactions) == 2
            assert all(t.acquirer == "cielo" for t in transactions)

    @pytest.mark.asyncio
    async def test_handle_authentication_failure(self, cielo_client: CieloEDIClient) -> None:
        with patch("aiohttp.ClientSession") as mock_session:
            mock_auth_response = AsyncMock()
            mock_auth_response.status = 401
            mock_auth_response.text.return_value = "Invalid credentials"

            mock_context = AsyncMock()
            mock_context.__aenter__.return_value.post.return_value.__aenter__.return_value = (
                mock_auth_response
            )
            mock_session.return_value = mock_context

            with pytest.raises(RuntimeError) as exc_info:
                await cielo_client.fetch_transactions(
                    tenant_id="tenant-123",
                    start_date=date(2025, 1, 1),
                    end_date=date(2025, 1, 31),
                )

            assert "Cielo authentication failed: 401" in str(exc_info.value)
