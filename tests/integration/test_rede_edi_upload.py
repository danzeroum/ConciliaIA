"""Integration tests for Rede EDI upload endpoint."""

from __future__ import annotations

import pytest
import pytest_asyncio
from httpx import AsyncClient
from fastapi import status

from src.api.main import app
from tests.utils.rede_edi_sample import sample_rede_edi_content


@pytest.fixture
def rede_edi_file() -> bytes:
    """Provide sample Rede EDI file content."""
    return sample_rede_edi_content().encode("utf-8")


@pytest_asyncio.fixture
async def async_client() -> AsyncClient:
    """Return an AsyncClient bound to the FastAPI app."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest_asyncio.fixture
async def auth_headers(async_client: AsyncClient, test_user) -> dict:
    """Authenticate and return authorization headers for tests."""
    response = await async_client.post(
        "/api/v1/auth/login",
        json={"email": "test@example.com", "password": "SecurePassword123!"},
    )
    assert response.status_code == status.HTTP_200_OK
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
class TestRedeEDIUpload:
    """Test suite for Rede EDI upload endpoint."""

    async def test_upload_edi_success(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        rede_edi_file: bytes,
    ):
        """Test successful EDI upload."""
        files = {"file": ("rede_test.txt", rede_edi_file, "text/plain")}

        response = await async_client.post(
            "/api/v1/transactions/import-edi?acquirer=rede",
            headers=auth_headers,
            files=files,
        )

        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert "imported" in data
        assert "failed" in data
        assert data["imported"] >= 0
        assert isinstance(data["failed"], int)

    async def test_upload_edi_without_auth(
        self,
        async_client: AsyncClient,
        rede_edi_file: bytes,
    ):
        """Test EDI upload without authentication."""
        files = {"file": ("rede_test.txt", rede_edi_file, "text/plain")}

        response = await async_client.post(
            "/api/v1/transactions/import-edi?acquirer=rede",
            files=files,
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_upload_invalid_edi(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
    ):
        """Test upload of invalid EDI file."""
        invalid_content = b"This is not a valid EDI file"

        files = {"file": ("invalid.txt", invalid_content, "text/plain")}

        response = await async_client.post(
            "/api/v1/transactions/import-edi?acquirer=rede",
            headers=auth_headers,
            files=files,
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Invalid" in response.json()["detail"]

    async def test_upload_edi_unsupported_acquirer(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        rede_edi_file: bytes,
    ):
        """Test upload with unsupported acquirer."""
        files = {"file": ("rede_test.txt", rede_edi_file, "text/plain")}

        response = await async_client.post(
            "/api/v1/transactions/import-edi?acquirer=unsupported",
            headers=auth_headers,
            files=files,
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "not implemented" in response.json()["detail"].lower()

    async def test_upload_edi_transactions_persisted(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        rede_edi_file: bytes,
    ):
        """Test that uploaded transactions are persisted in database."""
        # Upload EDI
        files = {"file": ("rede_test.txt", rede_edi_file, "text/plain")}

        upload_response = await async_client.post(
            "/api/v1/transactions/import-edi?acquirer=rede",
            headers=auth_headers,
            files=files,
        )

        assert upload_response.status_code == status.HTTP_200_OK
        imported_count = upload_response.json()["imported"]

        if imported_count > 0:
            # Verify transactions exist
            list_response = await async_client.get(
                "/api/v1/transactions?acquirer=rede",
                headers=auth_headers,
            )

            assert list_response.status_code == status.HTTP_200_OK
            transactions = list_response.json()["items"]

            # Should have at least the imported transactions
            assert len(transactions) >= imported_count

            # Verify acquirer is correct
            assert all(t["acquirer"] == "rede" for t in transactions)

    async def test_upload_edi_with_duplicate_nsu(
        self,
        async_client: AsyncClient,
        auth_headers: dict,
        rede_edi_file: bytes,
    ):
        """Test uploading same EDI twice (duplicate NSUs)."""
        files = {"file": ("rede_test.txt", rede_edi_file, "text/plain")}

        # First upload
        response1 = await async_client.post(
            "/api/v1/transactions/import-edi?acquirer=rede",
            headers=auth_headers,
            files=files,
        )
        assert response1.status_code == status.HTTP_200_OK
        imported1 = response1.json()["imported"]

        # Second upload (same file)
        files = {"file": ("rede_test.txt", rede_edi_file, "text/plain")}
        response2 = await async_client.post(
            "/api/v1/transactions/import-edi?acquirer=rede",
            headers=auth_headers,
            files=files,
        )
        assert response2.status_code == status.HTTP_200_OK

        # Should handle duplicates gracefully
        result2 = response2.json()
        assert result2["imported"] + result2["failed"] == imported1
