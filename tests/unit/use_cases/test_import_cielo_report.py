from datetime import date
from typing import List, Optional

import pytest

from src.application.use_cases.cielo_conciliator import (
    ImportCieloReportRequest,
    ImportCieloReportUseCase,
)
from src.infrastructure.acquirers import CieloAgilizaParser
from src.infrastructure.persistence.repositories import TransactionRepository


class FakeConciliatorClient:
    def __init__(self, payload: str) -> None:
        self.payload = payload
        self.calls: List[tuple[date, Optional[date]]] = []

    async def download_agiliza_report(
        self, *, start_date: date, end_date: date | None = None
    ) -> str:
        self.calls.append((start_date, end_date))
        return self.payload


class FakeTransactionRepository(TransactionRepository):
    def __init__(self) -> None:
        self.saved: List = []

    async def save(self, transaction):  # type: ignore[override]
        self.saved.append(transaction)

    async def find_by_id(self, tenant_id, transaction_id):  # type: ignore[override]
        return None

    async def delete(self, tenant_id, transaction_id):  # type: ignore[override]
        return None

    async def find_by_date_range(self, tenant_id, start_date, end_date):  # type: ignore[override]
        return []

    async def find_unmatched(self, tenant_id):  # type: ignore[override]
        return []

    async def find_by_acquirer(
        self, tenant_id, acquirer, start_date, end_date
    ):  # type: ignore[override]
        return []


@pytest.mark.asyncio
async def test_import_cielo_report_persists_transactions():
    csv_payload = (
        "NSU;Data Transação;Valor Bruto;Valor Líquido;Taxa MDR (%);Data Pagamento\n"
        "ABC123;01/03/2024;100,00;97,00;3,00%;02/03/2024\n"
    )

    client = FakeConciliatorClient(csv_payload)
    parser = CieloAgilizaParser()
    repository = FakeTransactionRepository()

    use_case = ImportCieloReportUseCase(
        client=client,
        parser=parser,
        transaction_repo=repository,
    )

    request = ImportCieloReportRequest(
        tenant_id="tenant-1", start_date=date(2024, 3, 1), end_date=date(2024, 3, 2)
    )

    response = await use_case.execute(request)

    assert response.imported == 1
    assert len(repository.saved) == 1
    assert repository.saved[0].tenant_id == "tenant-1"
    assert client.calls == [(date(2024, 3, 1), date(2024, 3, 2))]


@pytest.mark.asyncio
async def test_import_cielo_report_handles_empty_payload():
    client = FakeConciliatorClient("")
    parser = CieloAgilizaParser()
    repository = FakeTransactionRepository()

    use_case = ImportCieloReportUseCase(
        client=client,
        parser=parser,
        transaction_repo=repository,
    )

    response = await use_case.execute(
        ImportCieloReportRequest(tenant_id="tenant-1", start_date=date(2024, 3, 1))
    )

    assert response.imported == 0
    assert repository.saved == []
