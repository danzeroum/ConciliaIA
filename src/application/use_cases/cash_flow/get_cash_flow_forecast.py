"""Use case responsible for cash flow forecasts."""

"""Cash flow forecast use case implementation."""

from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal
from typing import Dict, List

from src.application.use_cases.interfaces import UseCase
from src.domain.entities import TransactionStatus
from src.domain.repositories import IAcquirerTransactionRepository


class GetCashFlowForecastRequest:
    """Request payload for the cash flow forecast use case."""

    def __init__(self, tenant_id: str, days_ahead: int = 30) -> None:
        self.tenant_id = tenant_id
        self.days_ahead = days_ahead


class CashFlowForecastResponse:
    """DTO returned with the calculated forecast data."""

    def __init__(
        self,
        total_expected: Decimal,
        total_received: Decimal,
        daily_forecast: List[Dict],
        summary_message: str,
    ) -> None:
        self.total_expected = total_expected
        self.total_received = total_received
        self.daily_forecast = daily_forecast
        self.summary_message = summary_message


class GetCashFlowForecastUseCase(
    UseCase[GetCashFlowForecastRequest, CashFlowForecastResponse]
):
    """Aggregates transactions to build a simple cash flow forecast."""

    def __init__(self, acquirer_transaction_repo: IAcquirerTransactionRepository) -> None:
        self.acquirer_transaction_repo = acquirer_transaction_repo

    async def execute(
        self, request: GetCashFlowForecastRequest
    ) -> CashFlowForecastResponse:
        """Execute the forecast calculation for the provided tenant."""

        start_date = date.today()
        end_date = start_date + timedelta(days=request.days_ahead)

        pending_transactions = await self.acquirer_transaction_repo.find_by_status_and_date_range(
            tenant_id=request.tenant_id,
            status=TransactionStatus.PENDING,
            start_date=start_date,
            end_date=end_date,
        )

        settled_transactions = await self.acquirer_transaction_repo.find_by_status_and_date_range(
            tenant_id=request.tenant_id,
            status=TransactionStatus.SETTLED,
            start_date=start_date,
            end_date=end_date,
        )

        daily_data: Dict[date, Dict[str, Decimal]] = {}

        for transaction in pending_transactions:
            day = self._resolve_settlement_day(transaction)
            daily_data.setdefault(day, {"expected": Decimal("0"), "received": Decimal("0")})
            daily_data[day]["expected"] += self._extract_amount(transaction)

        for transaction in settled_transactions:
            day = self._resolve_settlement_day(transaction)
            daily_data.setdefault(day, {"expected": Decimal("0"), "received": Decimal("0")})
            amount = self._extract_amount(transaction)
            daily_data[day]["expected"] += amount
            daily_data[day]["received"] += amount

        daily_forecast = [
            {
                "date": settlement_day.isoformat(),
                "date_formatted": settlement_day.strftime("%d/%m/%Y"),
                "expected": float(values["expected"]),
                "received": float(values["received"]),
            }
            for settlement_day, values in sorted(daily_data.items())
        ]

        total_expected = sum((entry["expected"] for entry in daily_forecast), start=0.0)
        total_received = sum((entry["received"] for entry in daily_forecast), start=0.0)

        summary_message = self._generate_summary_message(
            total_expected=Decimal(str(total_expected)),
            total_received=Decimal(str(total_received)),
            days_ahead=request.days_ahead,
        )

        return CashFlowForecastResponse(
            total_expected=Decimal(str(total_expected)),
            total_received=Decimal(str(total_received)),
            daily_forecast=daily_forecast,
            summary_message=summary_message,
        )

    def _resolve_settlement_day(self, transaction) -> date:
        settlement_date = getattr(transaction, "settlement_date", None)
        if settlement_date is None:
            return getattr(transaction, "transaction_date")
        if isinstance(settlement_date, date):
            return settlement_date
        return settlement_date.date()

    def _extract_amount(self, transaction) -> Decimal:
        amount = getattr(transaction, "net_amount", None)
        if amount is None:
            return Decimal("0")
        if hasattr(amount, "amount"):
            return Decimal(str(amount.amount))
        return Decimal(str(amount))

    def _generate_summary_message(
        self,
        total_expected: Decimal,
        total_received: Decimal,
        days_ahead: int,
    ) -> str:
        expected_str = self._format_currency(total_expected)
        received_str = self._format_currency(total_received)

        if total_received == 0:
            return f"Você vai receber {expected_str} nos próximos {days_ahead} dias"

        pending = total_expected - total_received
        if pending <= 0:
            return f"Você já recebeu {received_str} nos últimos {days_ahead} dias"

        pending_str = self._format_currency(pending)
        return f"Já recebeu {received_str}. Faltam {pending_str} para os próximos {days_ahead} dias"

    def _format_currency(self, value: Decimal) -> str:
        formatted = f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        return formatted
