"""Use case responsible for importing reports from Cielo Conciliator."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import List

from src.application.use_cases.interfaces import UseCase
from src.domain.entities import AcquirerTransaction
from src.infrastructure.acquirers import CieloAgilizaParser, CieloConciliatorClient
from src.infrastructure.persistence.repositories import TransactionRepository


@dataclass(slots=True)
class ImportCieloReportRequest:
    tenant_id: str
    start_date: date
    end_date: date | None = None


@dataclass(slots=True)
class ImportCieloReportResponse:
    imported: int
    transactions: List[AcquirerTransaction]


class ImportCieloReportUseCase(
    UseCase[ImportCieloReportRequest, ImportCieloReportResponse]
):
    """Download a report from Cielo Conciliator and persist the transactions."""

    def __init__(
        self,
        *,
        client: CieloConciliatorClient,
        parser: CieloAgilizaParser,
        transaction_repo: TransactionRepository,
    ) -> None:
        self._client = client
        self._parser = parser
        self._transaction_repo = transaction_repo

    async def execute(
        self, request: ImportCieloReportRequest
    ) -> ImportCieloReportResponse:
        payload = await self._client.download_agiliza_report(
            start_date=request.start_date, end_date=request.end_date
        )

        transactions = self._parser.parse(payload, request.tenant_id)

        for transaction in transactions:
            await self._transaction_repo.save(transaction)

        return ImportCieloReportResponse(imported=len(transactions), transactions=transactions)


__all__ = [
    "ImportCieloReportRequest",
    "ImportCieloReportResponse",
    "ImportCieloReportUseCase",
]
