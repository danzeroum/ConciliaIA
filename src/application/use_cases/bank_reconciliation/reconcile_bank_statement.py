"""Use case responsible for reconciling OFX bank statements."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Dict, List

import structlog

from src.application.use_cases.interfaces import UseCase
from src.domain.entities import (
    AcquirerTransaction,
    BankReconciliation,
    BankTransaction,
)
from src.domain.repositories import (
    IAcquirerTransactionRepository,
    IBankTransactionRepository,
)
from src.infrastructure.bank.ofx_parser import OFXParser

logger = structlog.get_logger(__name__)


@dataclass(slots=True)
class ReconcileBankStatementRequest:
    tenant_id: str
    ofx_content: str
    bank_account_id: str


@dataclass(slots=True)
class BankReconciliationResponse:
    total_transactions: int
    matched_count: int
    unmatched_count: int
    total_matched_amount: Decimal
    summary_message: str
    matches: List[Dict[str, object]]


class ReconcileBankStatementUseCase(
    UseCase[ReconcileBankStatementRequest, BankReconciliationResponse]
):
    """Confront OFX transactions with acquirer transactions using simple heuristics."""

    def __init__(
        self,
        acquirer_transaction_repo: IAcquirerTransactionRepository,
        bank_transaction_repo: IBankTransactionRepository,
    ) -> None:
        self._acquirer_transaction_repo = acquirer_transaction_repo
        self._bank_transaction_repo = bank_transaction_repo
        self._parser = OFXParser()
        self._logger = logger.bind(use_case="ReconcileBankStatementUseCase")

    async def execute(
        self, request: ReconcileBankStatementRequest
    ) -> BankReconciliationResponse:
        bank_transactions = await self._ingest_bank_transactions(request)

        if not bank_transactions:
            return BankReconciliationResponse(
                total_transactions=0,
                matched_count=0,
                unmatched_count=0,
                total_matched_amount=Decimal("0"),
                summary_message="Nenhuma transação bancária encontrada no OFX enviado.",
                matches=[],
            )

        period = self._calculate_date_range(bank_transactions)
        acquirer_transactions = await self._acquirer_transaction_repo.find_by_date_range(
            tenant_id=request.tenant_id,
            start_date=period["start"],
            end_date=period["end"],
        )

        matches = self._match_transactions(bank_transactions, acquirer_transactions)
        await self._persist_reconciliations(request.tenant_id, matches)

        matched_count = len(matches)
        unmatched_count = len(bank_transactions) - matched_count
        total_amount = sum(
            (match["bank_transaction"].amount for match in matches),
            Decimal("0"),
        )

        summary = self._build_summary_message(matched_count, unmatched_count, total_amount)

        return BankReconciliationResponse(
            total_transactions=len(bank_transactions),
            matched_count=matched_count,
            unmatched_count=unmatched_count,
            total_matched_amount=total_amount,
            summary_message=summary,
            matches=[self._serialise_match(match) for match in matches],
        )

    async def _ingest_bank_transactions(
        self, request: ReconcileBankStatementRequest
    ) -> List[BankTransaction]:
        try:
            parsed_transactions = self._parser.parse(request.ofx_content)
        except ValueError as exc:
            self._logger.warning("ofx_parse_failed", error=str(exc))
            raise

        bank_transactions: List[BankTransaction] = []
        for transaction_data in parsed_transactions:
            bank_transaction = BankTransaction.create(
                tenant_id=request.tenant_id,
                bank_account_id=request.bank_account_id,
                bank_transaction_id=str(transaction_data.get("bank_transaction_id", "")),
                transaction_date=transaction_data["transaction_date"],
                amount=Decimal(str(transaction_data["amount"])),
                type=str(transaction_data["type"]),
                memo=str(transaction_data.get("memo", "")),
                description_user_friendly=str(
                    transaction_data.get("description_user_friendly", "")
                ),
                check_number=str(transaction_data.get("check_number", "")),
            )
            stored = await self._bank_transaction_repo.create(bank_transaction)
            bank_transactions.append(stored)

        self._logger.info(
            "bank_transactions_ingested",
            count=len(bank_transactions),
            bank_account_id=request.bank_account_id,
        )
        return bank_transactions

    def _match_transactions(
        self,
        bank_transactions: List[BankTransaction],
        acquirer_transactions: List[AcquirerTransaction],
    ) -> List[Dict[str, object]]:
        matches: List[Dict[str, object]] = []
        matched_acquirer_ids: set[str] = set()

        for bank_txn in bank_transactions:
            if bank_txn.amount <= 0:
                continue

            best_candidate: Dict[str, object] | None = None
            best_confidence = 0.0

            for acq_txn in acquirer_transactions:
                if acq_txn.id in matched_acquirer_ids:
                    continue

                confidence = self._calculate_match_confidence(bank_txn, acq_txn)
                if confidence > best_confidence and confidence >= 0.85:
                    best_candidate = {
                        "bank_transaction": bank_txn,
                        "acquirer_transaction": acq_txn,
                        "confidence": confidence,
                    }
                    best_confidence = confidence

            if best_candidate:
                matched_acquirer_ids.add(best_candidate["acquirer_transaction"].id)
                matches.append(best_candidate)

        self._logger.info(
            "bank_transactions_matched",
            candidate_bank=len(bank_transactions),
            candidate_acquirer=len(acquirer_transactions),
            matches=len(matches),
        )
        return matches

    def _calculate_match_confidence(
        self, bank_txn: BankTransaction, acq_txn: AcquirerTransaction
    ) -> float:
        net_amount = (
            acq_txn.net_amount.amount
            if getattr(acq_txn, "net_amount", None) is not None
            else acq_txn.amount.amount
        )

        amount_diff = abs(bank_txn.amount - net_amount)
        if amount_diff < Decimal("0.10"):
            confidence = 0.60
        elif amount_diff < Decimal("1.00"):
            confidence = 0.30
        else:
            return 0.0

        settlement_reference = (
            acq_txn.settlement_date or acq_txn.transaction_date
        )
        date_diff = abs((bank_txn.transaction_date.date() - settlement_reference).days)
        if date_diff == 0:
            confidence += 0.30
        elif date_diff <= 1:
            confidence += 0.20
        elif date_diff <= 3:
            confidence += 0.10

        memo = (bank_txn.memo or "").lower()
        if memo:
            if getattr(acq_txn, "nsu", None) and str(acq_txn.nsu).lower() in memo:
                confidence += 0.10
            elif getattr(acq_txn, "authorization_code", None) and str(
                acq_txn.authorization_code
            ).lower() in memo:
                confidence += 0.10

        return confidence

    async def _persist_reconciliations(
        self, tenant_id: str, matches: List[Dict[str, object]]
    ) -> None:
        for match in matches:
            bank_txn: BankTransaction = match["bank_transaction"]
            acq_txn: AcquirerTransaction = match["acquirer_transaction"]
            reconciliation = BankReconciliation.create(
                tenant_id=tenant_id,
                bank_transaction_id=bank_txn.id,
                acquirer_transaction_id=acq_txn.id,
                match_confidence=match["confidence"],
            )
            self._logger.debug(
                "bank_reconciliation_created",
                bank_transaction_id=str(reconciliation.bank_transaction_id),
                acquirer_transaction_id=reconciliation.acquirer_transaction_id,
                confidence=reconciliation.match_confidence,
            )

    def _calculate_date_range(
        self, transactions: List[BankTransaction]
    ) -> Dict[str, date]:
        dates = [txn.transaction_date.date() for txn in transactions]
        return {
            "start": min(dates) - timedelta(days=3),
            "end": max(dates) + timedelta(days=3),
        }

    def _build_summary_message(
        self, matched: int, unmatched: int, total_amount: Decimal
    ) -> str:
        amount_str = f"R$ {total_amount:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        if matched == 0:
            return "Nenhum pagamento foi conciliado automaticamente."
        if unmatched == 0:
            return f"✅ Todos os {matched} pagamentos foram confirmados ({amount_str})"
        return (
            f"✅ {matched} pagamentos confirmados ({amount_str}). "
            f"⚠️ {unmatched} precisam de revisão"
        )

    def _serialise_match(self, match: Dict[str, object]) -> Dict[str, object]:
        bank_txn: BankTransaction = match["bank_transaction"]
        return {
            "bank_transaction_id": str(bank_txn.id),
            "acquirer_transaction_id": match["acquirer_transaction"].id,
            "amount": float(bank_txn.amount),
            "confidence": match["confidence"],
            "description": f"Pagamento de {self._format_currency(bank_txn.amount)} confirmado",
        }

    def _format_currency(self, value: Decimal) -> str:
        return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


__all__ = [
    "ReconcileBankStatementUseCase",
    "ReconcileBankStatementRequest",
    "BankReconciliationResponse",
]
