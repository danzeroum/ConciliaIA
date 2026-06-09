"""Unit tests for RedeAPIParser using a real sandbox sales response.

The fixture is a representative subset of an actual
``GET /merchant-statement/v1/sales`` response, covering: an integer
authorizationCode, a strAuthorizationCode, a DEBIT sale, a CANCELLED sale, a
row without ``saleDate`` (movementDate fallback) and a repeated NSU (which must
not be de-duplicated).
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from src.domain.entities import TransactionStatus
from src.infrastructure.acquirers import RedeAPIParser

SAMPLE = {
    "content": {
        "transactions": [
            {
                "status": "APPROVED", "nsu": 879555119, "captureType": "ECOMMERCE",
                "mdrAmount": 2.17, "mdrFee": 1.84, "netAmount": 115.95, "amount": 118.12,
                "authorizationCode": 441488, "cardNumber": "230744******1322",
                "movementDate": "2026-05-20", "saleDate": "2026-05-20", "brandCode": 1,
                "modality": {"type": "CREDIT"},
            },
            {
                "status": "APPROVED", "nsu": 377073583, "captureType": "ECOMMERCE",
                "mdrAmount": 14.59, "mdrFee": 2, "netAmount": 715.11, "amount": 729.7,
                "authorizationCode": 0, "strAuthorizationCode": "D268971",
                "cardNumber": "549167******0973", "movementDate": "2026-05-20",
                "saleDate": "2026-05-20", "brandCode": 1, "modality": {"type": "CREDIT"},
            },
            {
                "status": "APPROVED", "nsu": 4732688, "captureType": "POS",
                "mdrAmount": 2.35, "mdrFee": 1.59, "netAmount": 145.65, "amount": 148,
                "authorizationCode": 0, "strAuthorizationCode": "D118617",
                "cardNumber": "520977******2740", "movementDate": "2026-05-20",
                "saleDate": "2026-05-20", "brandCode": 1, "modality": {"type": "DEBIT"},
            },
            {
                "status": "CANCELLED", "nsu": 13178011, "captureType": "ECOMMERCE",
                "mdrAmount": 3.48, "mdrFee": 1.85, "netAmount": 184.85, "amount": 188.33,
                "authorizationCode": 144147, "cardNumber": "550209******9666",
                "movementDate": "2026-05-20", "saleDate": "2026-05-20", "brandCode": 1,
                "modality": {"type": "CREDIT"},
            },
            {
                # no saleDate -> movementDate is used
                "status": "APPROVED", "nsu": 888533335045, "captureType": "POS",
                "mdrAmount": 407.01, "mdrFee": 4, "netAmount": 9768.32, "amount": 10175.33,
                "authorizationCode": 140700, "cardNumber": "548045******3790",
                "movementDate": "2026-05-20", "brandCode": 1, "modality": {"type": "CREDIT"},
            },
            {
                # repeated NSU 4570994 (entry A)
                "status": "APPROVED", "nsu": 4570994, "captureType": "POS",
                "mdrAmount": 6.24, "mdrFee": 2.6, "netAmount": 233.76, "amount": 240,
                "authorizationCode": 677556, "cardNumber": "625094******0005",
                "movementDate": "2026-05-20", "saleDate": "2026-05-20", "brandCode": 1,
                "modality": {"type": "CREDIT"},
            },
            {
                # repeated NSU 4570994 (entry B, different amount/card)
                "status": "APPROVED", "nsu": 4570994, "captureType": "POS",
                "mdrAmount": 3.85, "mdrFee": 2.49, "netAmount": 150.95, "amount": 154.8,
                "authorizationCode": 67214, "cardNumber": "516292******4480",
                "movementDate": "2026-05-20", "saleDate": "2026-05-20", "brandCode": 1,
                "modality": {"type": "CREDIT"},
            },
        ]
    },
    "cursor": {"hasNextKey": False},
}


def _by_nsu(transactions, nsu):
    return [t for t in transactions if t.nsu.value == nsu]


def test_parses_all_rows():
    transactions = RedeAPIParser().parse(SAMPLE, "tenant-1")
    assert len(transactions) == 7
    assert all(str(t.acquirer) == "rede" for t in transactions)
    assert all(t.tenant_id == "tenant-1" for t in transactions)


def test_maps_monetary_fields_and_rate():
    transactions = RedeAPIParser().parse(SAMPLE, "tenant-1")
    txn = _by_nsu(transactions, "879555119")[0]
    assert txn.amount.amount == Decimal("118.12")        # gross = amount
    assert txn.mdr_amount.amount == Decimal("2.17")       # MDR in BRL = mdrAmount
    assert txn.net_amount.amount == Decimal("115.95")     # net = netAmount
    assert txn.mdr_rate.value == Decimal("0.0184")        # mdrFee 1.84% -> 0.0184
    assert txn.transaction_date == date(2026, 5, 20)
    assert txn.card_last_4 == "1322"
    assert str(txn.authorization_code) == "441488"
    assert txn.status == TransactionStatus.APPROVED


def test_prefers_string_authorization_code():
    transactions = RedeAPIParser().parse(SAMPLE, "tenant-1")
    txn = _by_nsu(transactions, "377073583")[0]
    assert str(txn.authorization_code) == "D268971"


def test_maps_cancelled_status():
    transactions = RedeAPIParser().parse(SAMPLE, "tenant-1")
    txn = _by_nsu(transactions, "13178011")[0]
    assert txn.status == TransactionStatus.CANCELLED


def test_falls_back_to_movement_date():
    transactions = RedeAPIParser().parse(SAMPLE, "tenant-1")
    txn = _by_nsu(transactions, "888533335045")[0]
    assert txn.transaction_date == date(2026, 5, 20)


def test_keeps_repeated_nsu_rows():
    transactions = RedeAPIParser().parse(SAMPLE, "tenant-1")
    repeated = _by_nsu(transactions, "4570994")
    assert len(repeated) == 2
    assert {t.amount.amount for t in repeated} == {Decimal("240.00"), Decimal("154.80")}


def test_handles_empty_and_unknown_payloads():
    assert RedeAPIParser().parse({"content": {"transactions": []}}, "t") == []
    assert RedeAPIParser().parse({"unexpected": 1}, "t") == []
