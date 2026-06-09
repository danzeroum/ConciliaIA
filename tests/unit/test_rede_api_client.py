"""Unit tests for the env-configurable Rede REST API client.

Only the configuration resolution and the (provisional) response mapping are
covered here — the live HTTP contract must be validated against Rede's real
authenticated API.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from src.infrastructure.acquirers import RedeAPIClient

_REQUIRED = ("REDE_API_BASE_URL", "REDE_CLIENT_ID", "REDE_CLIENT_SECRET")


def test_requires_credentials(monkeypatch):
    for var in (*_REQUIRED, "REDE_SCOPE", "REDE_TOKEN_PATH", "REDE_TRANSACTIONS_PATH"):
        monkeypatch.delenv(var, raising=False)
    with pytest.raises(ValueError):
        RedeAPIClient()


def test_reads_config_from_env(monkeypatch):
    monkeypatch.setenv("REDE_API_BASE_URL", "https://rl7-sandbox-api.useredecloud.com.br/")
    monkeypatch.setenv("REDE_CLIENT_ID", "cid")
    monkeypatch.setenv("REDE_CLIENT_SECRET", "secret")
    monkeypatch.delenv("REDE_TOKEN_PATH", raising=False)
    monkeypatch.delenv("REDE_TRANSACTIONS_PATH", raising=False)

    client = RedeAPIClient()

    assert client.base_url == "https://rl7-sandbox-api.useredecloud.com.br"  # trailing / stripped
    assert client.client_id == "cid"
    assert client.client_secret == "secret"
    assert client.token_path == "/oauth/token"
    assert client.transactions_path == "/transactions"


def test_explicit_params_override_env(monkeypatch):
    monkeypatch.setenv("REDE_API_BASE_URL", "https://env-host")
    monkeypatch.setenv("REDE_CLIENT_ID", "env-id")
    monkeypatch.setenv("REDE_CLIENT_SECRET", "env-secret")

    client = RedeAPIClient(
        base_url="https://explicit-host",
        client_id="explicit-id",
        client_secret="explicit-secret",
        transactions_path="/sales",
    )

    assert client.base_url == "https://explicit-host"
    assert client.client_id == "explicit-id"
    assert client.transactions_path == "/sales"


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
    assert txn.tenant_id == "tenant-1"
    assert txn.transaction_date == date(2026, 6, 1)
    assert txn.amount.amount == Decimal("100.00")
    assert txn.net_amount.amount == Decimal("97.50")


def test_parse_transactions_skips_malformed_rows():
    client = RedeAPIClient(base_url="https://x", client_id="a", client_secret="b")
    rows = [{"nsu": "1"}, {"transactionDate": "bad"}]  # both missing required fields

    assert client._parse_transactions(rows, "tenant-1") == []
