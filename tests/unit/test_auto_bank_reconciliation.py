from datetime import date
from decimal import Decimal
import pytest

from src.application.use_cases.auto_bank_reconciliation import (
    AutoBankReconciliationRequest,
    AutoBankReconciliationUseCase,
    BankPayment,
)
from src.domain.entities import Settlement, SettlementStatus
from src.domain.value_objects import Money


class DummySettlementRepository:
    def __init__(self, settlements):
        self._settlements = settlements
        self.saved = []

    async def find_by_status(self, tenant_id, status):
        return [s for s in self._settlements if s.status == status]

    async def save(self, settlement):
        self.saved.append(settlement)

    async def find_delayed(self, tenant_id):  # pragma: no cover - unused
        return []


@pytest.mark.asyncio
async def test_auto_bank_reconciliation_matches_payment() -> None:
    settlement = Settlement(
        id="settlement-1",
        transaction_id="txn-1",
        tenant_id="tenant-1",
        expected_date=date(2024, 1, 15),
        net_amount=Money(Decimal("1000.00")),
        status=SettlementStatus.PENDING,
    )
    repository = DummySettlementRepository([settlement])
    use_case = AutoBankReconciliationUseCase(repository)  # type: ignore[arg-type]

    request = AutoBankReconciliationRequest(
        tenant_id="tenant-1",
        payments=[BankPayment(payment_date=date(2024, 1, 15), amount=Decimal("1000.00"))],
    )

    response = await use_case.execute(request)

    assert len(response.matched) == 1
    assert response.matched[0].settlement_id == "settlement-1"
    assert settlement.status == SettlementStatus.PAID
