"""Unit tests for the env-configurable Rede "Gestão de Vendas" API client.

The request contract (token + sales endpoints/params) is verified against Rede's
Postman collection; only the response field mapping remains provisional, so the
parse tests exercise the (provisional) shape and the resilient row extraction.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from src.infrastructure.acquirers import RedeAPIClient

_VARS = (
    "REDE_API_BASE_URL",
    "REDE_CLIENT_ID",
    "REDE_CLIENT_SECRET",
    "REDE_SCOPE",
    "REDE_TOKEN_PATH",
    "REDE_SALES_PATH",
    "REDE_PARENT_COMPANY_NUMBER",
    "REDE_SUBSIDIARIES",
)


def _clear(monkeypatch):
    for var in _VARS:
        monkeypatch.delenv(var, raising=False)


def test_requires_credentials(monkeypatch):
    _clear(monkeypatch)
    with pytest.raises(ValueError):
        RedeAPIClient()


def test_reads_config_from_env(monkeypatch):
    _clear(monkeypatch)
    monkeypatch.setenv("REDE_API_BASE_URL", "https://rl7-sandbox-api.useredecloud.com.br/")
    monkeypatch.setenv("REDE_CLIENT_ID", "cid")
    monkeypatch.setenv("REDE_CLIENT_SECRET", "secret")
    monkeypatch.setenv("REDE_PARENT_COMPANY_NUMBER", "13381369")

    client = RedeAPIClient()

    assert client.base_url == "https://rl7-sandbox-api.useredecloud.com.br"  # trailing / stripped
    assert client.client_id == "cid"
    assert client.parent_company_number == "13381369"
    assert client.subsidiaries == "13381369"  # defaults to the parent company number
    assert client.token_path == "/oauth2/token"
    assert client.sales_path == "/merchant-statement/v1/sales"


def test_explicit_params_override_env(monkeypatch):
    _clear(monkeypatch)
    monkeypatch.setenv("REDE_API_BASE_URL", "https://env-host")
    monkeypatch.setenv("REDE_CLIENT_ID", "env-id")
    monkeypatch.setenv("REDE_CLIENT_SECRET", "env-secret")

    client = RedeAPIClient(
        base_url="https://explicit",
        client_id="a",
        client_secret="b",
        parent_company_number="999",
        sales_path="/custom/sales",
    )

    assert client.base_url == "https://explicit"
    assert client.client_id == "a"
    assert client.parent_company_number == "999"
    assert client.sales_path == "/custom/sales"


def test_extract_rows_handles_wrappers_and_lists():
    assert RedeAPIClient._extract_rows({"content": [{"a": 1}]}) == [{"a": 1}]
    assert RedeAPIClient._extract_rows({"sales": [{"b": 2}]}) == [{"b": 2}]
    assert RedeAPIClient._extract_rows([{"c": 3}]) == [{"c": 3}]
    assert RedeAPIClient._extract_rows({"unknown": 1}) == []


async def test_fetch_transactions_requires_parent_company_number(monkeypatch):
    monkeypatch.delenv("REDE_PARENT_COMPANY_NUMBER", raising=False)
    monkeypatch.delenv("REDE_SUBSIDIARIES", raising=False)
    client = RedeAPIClient(base_url="https://x", client_id="a", client_secret="b")

    with pytest.raises(ValueError):
        await client.fetch_transactions("tenant-1", date(2026, 6, 1), date(2026, 6, 9))


def test_parse_transactions_maps_fields():
    client = RedeAPIClient(base_url="https://x", client_id="a", client_secret="b")
    rows = [
        {
            "nsu": "123456",
            "transactionDate": "2026-06-01",
            "grossAmount": "100.00",
            "mdrFee": "2.50",
            "netAmount": "97.50",
        }
    ]

    transactions = client._parse_transactions(rows, "tenant-1")

    assert len(transactions) == 1
    txn = transactions[0]
    assert txn.nsu.value == "123456"
    assert txn.acquirer.value == "rede"
    assert txn.transaction_date == date(2026, 6, 1)
    assert txn.amount.amount == Decimal("100.00")
    assert txn.net_amount.amount == Decimal("97.50")


def test_parse_transactions_skips_malformed_rows():
    client = RedeAPIClient(base_url="https://x", client_id="a", client_secret="b")
    rows = [{"nsu": "1"}, {"transactionDate": "bad"}]
    assert client._parse_transactions(rows, "tenant-1") == []
