from datetime import date

import httpx
import pytest

from src.infrastructure.acquirers import (
    CieloConciliatorClient,
    CieloConciliatorError,
)


@pytest.mark.asyncio
async def test_download_agiliza_report_success():
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/oauth/token":
            return httpx.Response(200, json={"access_token": "token", "expires_in": 3600})
        if request.url.path == "/conciliator/agiliza/reports":
            assert request.headers["Authorization"] == "Bearer token"
            assert request.url.params["start_date"] == "2024-03-01"
            assert request.url.params["end_date"] == "2024-03-05"
            return httpx.Response(
                200,
                text="csv-data",
                headers={"content-type": "text/csv"},
            )
        raise AssertionError(f"Unexpected path: {request.url.path}")

    transport = httpx.MockTransport(handler)
    http_client = httpx.AsyncClient(transport=transport, base_url="https://api.test")

    client = CieloConciliatorClient(
        base_url="https://api.test",
        client_id="abc",
        client_secret="def",
        http_client=http_client,
    )

    payload = await client.download_agiliza_report(
        start_date=date(2024, 3, 1), end_date=date(2024, 3, 5)
    )

    assert payload == "csv-data"

    await client.aclose()
    await http_client.aclose()


@pytest.mark.asyncio
async def test_download_agiliza_report_handles_auth_error():
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/oauth/token":
            return httpx.Response(401, json={"error": "invalid_client"})
        raise AssertionError("Report request should not be called when auth fails")

    http_client = httpx.AsyncClient(
        transport=httpx.MockTransport(handler), base_url="https://api.test"
    )

    client = CieloConciliatorClient(
        base_url="https://api.test",
        client_id="abc",
        client_secret="def",
        http_client=http_client,
    )

    with pytest.raises(CieloConciliatorError):
        await client.download_agiliza_report(start_date=date(2024, 3, 1))

    await client.aclose()
    await http_client.aclose()


@pytest.mark.asyncio
async def test_download_agiliza_report_validates_date_range():
    def handler(_: httpx.Request) -> httpx.Response:
        raise AssertionError("HTTP request should not be executed when validation fails")

    http_client = httpx.AsyncClient(transport=httpx.MockTransport(handler))

    client = CieloConciliatorClient(
        base_url="https://api.test",
        client_id="abc",
        client_secret="def",
        http_client=http_client,
    )

    with pytest.raises(ValueError):
        await client.download_agiliza_report(
            start_date=date(2024, 3, 5), end_date=date(2024, 3, 1)
        )

    await client.aclose()
    await http_client.aclose()
