"""Use case to reconcile bank payments with pending settlements."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Iterable, List

import structlog

from src.domain.entities import Settlement, SettlementStatus
from src.infrastructure.persistence.repositories import SettlementRepository

logger = structlog.get_logger(__name__)


@dataclass(slots=True)
class BankPayment:
    payment_date: date
    amount: Decimal
    reference: str | None = None


@dataclass(slots=True)
class AutoBankReconciliationRequest:
    tenant_id: str
    payments: List[BankPayment]
    tolerance_days: int = 2
    amount_tolerance: Decimal = Decimal("0.50")


@dataclass(slots=True)
class MatchedPayment:
    payment_date: date
    amount: Decimal
    settlement_id: str
    expected_date: date


@dataclass(slots=True)
class AutoBankReconciliationResponse:
    matched: List[MatchedPayment]
    unmatched: List[BankPayment]


class AutoBankReconciliationUseCase:
    """Match bank payments to pending settlements."""

    def __init__(self, settlement_repository: SettlementRepository) -> None:
        self._settlement_repository = settlement_repository
        self._logger = logger.bind(use_case="AutoBankReconciliationUseCase")

    async def execute(
        self, request: AutoBankReconciliationRequest
    ) -> AutoBankReconciliationResponse:
        pending = await self._settlement_repository.find_by_status(
            request.tenant_id, SettlementStatus.PENDING
        )
        delayed = await self._settlement_repository.find_by_status(
            request.tenant_id, SettlementStatus.DELAYED
        )
        candidates = list(pending) + list(delayed)

        matched: List[MatchedPayment] = []
        unmatched: List[BankPayment] = []
        used: set[str] = set()

        for payment in request.payments:
            settlement = self._match_payment(payment, candidates, request.tolerance_days, request.amount_tolerance, used)
            if settlement:
                used.add(settlement.id)
                settlement.actual_date = payment.payment_date
                settlement.status = SettlementStatus.PAID
                await self._settlement_repository.save(settlement)
                matched.append(
                    MatchedPayment(
                        payment_date=payment.payment_date,
                        amount=payment.amount,
                        settlement_id=settlement.id,
                        expected_date=settlement.expected_date,
                    )
                )
            else:
                unmatched.append(payment)

        self._logger.info(
            "auto_bank_reconciliation_completed",
            tenant_id=request.tenant_id,
            matched=len(matched),
            unmatched=len(unmatched),
        )

        return AutoBankReconciliationResponse(matched=matched, unmatched=unmatched)

    def _match_payment(
        self,
        payment: BankPayment,
        settlements: Iterable[Settlement],
        tolerance_days: int,
        amount_tolerance: Decimal,
        used: set[str],
    ) -> Settlement | None:
        for candidate in settlements:
            if candidate.id in used:
                continue
            delta_days = abs((payment.payment_date - candidate.expected_date).days)
            if delta_days > tolerance_days:
                continue
            amount_diff = abs(candidate.net_amount.amount - payment.amount)
            if amount_diff > amount_tolerance:
                continue
            return candidate
        return None


__all__ = [
    "AutoBankReconciliationUseCase",
    "AutoBankReconciliationRequest",
    "AutoBankReconciliationResponse",
    "BankPayment",
]
