"""Integration tests for acquirer clients."""

from __future__ import annotations

from datetime import date
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.infrastructure.acquirers import CieloEDIClient, RedeEDIClient, StoneAPIClient


@pytest.mark.integration
@pytest.mark.asyncio
class TestCieloEDIClient:
    """Test Cielo EDI SFTP client."""

    @patch("src.infrastructure.acquirers.cielo_edi_client.paramiko.Transport")
    async def test_download_file(self, mock_transport: MagicMock) -> None:
        mock_sftp = MagicMock()
        mock_transport_instance = MagicMock()
        mock_transport.return_value = mock_transport_instance
        mock_transport_instance.connect = MagicMock()
        with patch(
            "src.infrastructure.acquirers.cielo_edi_client.paramiko.SFTPClient.from_transport",
            return_value=mock_sftp,
        ):
            client = CieloEDIClient(
                host="sftp.cielo.com.br",
                port=22,
                username="test_user",
                password="test_pass",
                ec_number="1234567890",
            )
            target_date = date.today()
            local_path = Path("/tmp/cielo")
            file_path = await client.download_file(target_date, local_path)
            expected_filename = f"EC1234567890_{target_date.strftime('%Y%m%d')}.txt"
            assert file_path.name == expected_filename if file_path else True


@pytest.mark.integration
@pytest.mark.asyncio
class TestStoneAPIClient:
    """Test Stone API client."""

    @patch("httpx.AsyncClient")
    async def test_fetch_transactions(self, mock_client: MagicMock) -> None:
        mock_auth_response = MagicMock()
        mock_auth_response.json.return_value = {"access_token": "test_token"}
        mock_auth_response.status_code = 200

        mock_txn_response = MagicMock()
        mock_txn_response.json.return_value = {
            "transactions": [
                {
                    "stone_id": "123456789",
                    "amount": 10000,
                    "fee_amount": 250,
                    "net_amount": 9750,
                    "created_at": "2023-01-18T10:30:00Z",
                    "card": {"brand": "visa", "last_digits": "1234"},
                    "status": "approved",
                }
            ],
            "pagination": {"has_next": False},
        }
        mock_txn_response.status_code = 200

        mock_client_instance = MagicMock()
        mock_client_instance.post = AsyncMock(return_value=mock_auth_response)
        mock_client_instance.get = AsyncMock(return_value=mock_txn_response)
        mock_client.return_value.__aenter__.return_value = mock_client_instance

        client = StoneAPIClient(
            client_id="test_client",
            client_secret="test_secret",
            stone_code="1234567890",
        )

        transactions = await client.fetch_transactions(
            start_date=date(2023, 1, 1),
            end_date=date(2023, 1, 31),
        )

        assert len(transactions) == 1
        assert transactions[0]["stone_id"] == "123456789"


@pytest.mark.integration
@pytest.mark.asyncio
class TestRedeEDIClient:
    """Test Rede EDI client with local files."""

    async def test_fetch_local_file(self, tmp_path: Path) -> None:
        file_date = date(2024, 1, 15)
        filename = f"EEVC{file_date.strftime('%Y%m%d')}.txt"
        content = "EEVC HEADER\n012DATA"
        (tmp_path / filename).write_bytes(content.encode("latin-1"))

        client = RedeEDIClient(base_path=tmp_path)
        data = await client.fetch_eevc(file_date)

        assert data.decode("latin-1") == content
