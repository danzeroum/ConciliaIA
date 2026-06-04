from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import List
from uuid import uuid4

import pytest

from src.application.use_cases.bank_reconciliation import (
    BankReconciliationResponse,
    ReconcileBankStatementRequest,
    ReconcileBankStatementUseCase,
)
from src.domain.entities import AcquirerTransaction
from src.domain.repositories import IAcquirerTransactionRepository, IBankTransactionRepository
from src.domain.value_objects import Money


class FakeBankTransactionRepository(IBankTransactionRepository):
    def __init__(self) -> None:
        self.saved: List = []

    async def create(self, transaction):  # type: ignore[override]
        self.saved.append(transaction)
        return transaction


class FakeAcquirerTransactionRepository(IAcquirerTransactionRepository):
    def __init__(self, transactions: List[AcquirerTransaction]) -> None:
        self.transactions = transactions

    async def find_by_status_and_date_range(self, *args, **kwargs):  # type: ignore[override]
        raise NotImplementedError

    async def find_by_date_range(self, *args, **kwargs):  # type: ignore[override]
        return self.transactions

    async def find_delayed_settlements(self, *args, **kwargs):  # type: ignore[override]
        return []

    async def find_chargebacks(self, *args, **kwargs):  # type: ignore[override]
        return []


@pytest.mark.asyncio
async def test_reconcile_bank_statement_matches_credit_transaction():
    ofx_content = """
    <OFX>
      <BANKMSGSRSV1>
        <STMTTRNRS>
          <STMTRS>
            <BANKTRANLIST>
              <STMTTRN>
                <TRNTYPE>CREDIT</TRNTYPE>
                <DTPOSTED>20240102120000</DTPOSTED>
                <TRNAMT>1500.00</TRNAMT>
                <FITID>ABC123</FITID>
                <MEMO>PAGAMENTO NSU 999999</MEMO>
              </STMTTRN>
            </BANKTRANLIST>
          </STMTRS>
        </STMTTRNRS>
      </BANKMSGSRSV1>
    </OFX>
    """

    acquirer_txn = AcquirerTransaction(
        id=str(uuid4()),
        tenant_id="tenant-1",
        acquirer="stone",
        nsu="999999",
        amount=Money(Decimal("1530.00"), "BRL"),
        transaction_date=date(2024, 1, 2),
        settlement_date=date(2024, 1, 2),
        net_amount=Money(Decimal("1500.00"), "BRL"),
        status="settled",
    )

    bank_repo = FakeBankTransactionRepository()
    acquirer_repo = FakeAcquirerTransactionRepository([acquirer_txn])

    use_case = ReconcileBankStatementUseCase(
        acquirer_transaction_repo=acquirer_repo,
        bank_transaction_repo=bank_repo,
    )

    request = ReconcileBankStatementRequest(
        tenant_id="tenant-1",
        ofx_content=ofx_content,
        bank_account_id="account-123",
    )

    response = await use_case.execute(request)

    assert isinstance(response, BankReconciliationResponse)
    assert response.total_transactions == 1
    assert response.matched_count == 1
    assert response.unmatched_count == 0
    assert response.total_matched_amount == Decimal("1500.00")
    assert "confirmados" in response.summary_message.lower()
    assert len(bank_repo.saved) == 1
    assert response.matches[0]["confidence"] >= 0.9
    assert response.matches[0]["bank_transaction_id"]


@pytest.mark.asyncio
async def test_reconcile_bank_statement_handles_invalid_ofx():
    bank_repo = FakeBankTransactionRepository()
    acquirer_repo = FakeAcquirerTransactionRepository([])

    use_case = ReconcileBankStatementUseCase(
        acquirer_transaction_repo=acquirer_repo,
        bank_transaction_repo=bank_repo,
    )

    request = ReconcileBankStatementRequest(
        tenant_id="tenant-1",
        ofx_content="",
        bank_account_id="account-123",
    )

    with pytest.raises(ValueError):
        await use_case.execute(request)
