"""Integration tests covering the reconciliation use case end-to-end."""

from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal
from unittest.mock import AsyncMock

import pytest

from src.application.services import AnomalyDetectionService, MatchingService
from src.application.strategies import ExactMatcher, FuzzyMatcher, MLMatcher
from src.application.use_cases.reconcile_transactions import (
    ReconcileTransactionsUseCase,
)
from src.domain.entities import AcquirerTransaction, Sale
from src.domain.value_objects import Money


@pytest.mark.integration
class TestReconciliationFlow:
    @pytest.fixture
    def use_case(self) -> ReconcileTransactionsUseCase:
        sale_repo = AsyncMock()
        transaction_repo = AsyncMock()
        match_repo = AsyncMock()
        divergence_repo = AsyncMock()

        matching_service = MatchingService(
            exact_matcher=ExactMatcher(),
            fuzzy_matcher=FuzzyMatcher(),
            ml_matcher=MLMatcher(model_path=None),
        )

        anomaly_service = AnomalyDetectionService()

        return ReconcileTransactionsUseCase(
            sale_repo=sale_repo,
            transaction_repo=transaction_repo,
            match_repo=match_repo,
            divergence_repo=divergence_repo,
            matching_service=matching_service,
            anomaly_service=anomaly_service,
        )

    @pytest.mark.asyncio
    async def test_complete_reconciliation_happy_path(
        self, use_case: ReconcileTransactionsUseCase
    ) -> None:
        tenant_id = "tenant-123"
        start_date = date(2025, 1, 1)
        end_date = date(2025, 1, 31)

        sales = [
            Sale(
                id=f"sale-{index:03d}",
                tenant_id=tenant_id,
                nsu=f"NSU{index:06d}",
                amount=Money(Decimal(f"{100 + index}.00")),
                date=date(2025, 1, 15),
                payment_method="credit_1x",
            )
            for index in range(10)
        ]

        transactions = [
            AcquirerTransaction(
                id=f"txn-{index:03d}",
                tenant_id=tenant_id,
                acquirer="cielo",
                nsu=f"NSU{index:06d}",
                amount=Money(Decimal(f"{100 + index}.00")),
                transaction_date=date(2025, 1, 15),
                mdr_amount=Money(Decimal("3.00")),
                net_amount=Money(Decimal(f"{97 + index}.00")),
            )
            for index in range(10)
        ]

        use_case.sale_repo.find_by_date_range.return_value = sales
        use_case.transaction_repo.find_by_date_range.return_value = transactions

        result = await use_case.execute(
            tenant_id=tenant_id,
            start_date=start_date,
            end_date=end_date,
        )

        assert result.matched_count == 10
        assert len(result.divergences) == 0
        assert result.accuracy == Decimal("1")
        assert result.precision == Decimal("1.0")
        assert use_case.match_repo.save.call_count == 10
        assert use_case.divergence_repo.save.call_count == 0

    @pytest.mark.asyncio
    async def test_reconciliation_with_divergences(
        self, use_case: ReconcileTransactionsUseCase
    ) -> None:
        tenant_id = "tenant-456"
        today = date.today()

        matched_sales = [
            Sale(
                id=f"sale-match-{index}",
                tenant_id=tenant_id,
                nsu=f"MATCH{index}",
                amount=Money(Decimal("100.00")),
                date=today,
                payment_method="credit_1x",
            )
            for index in range(5)
        ]

        missing_sales = [
            Sale(
                id=f"sale-missing-{index}",
                tenant_id=tenant_id,
                nsu=f"MISSING{index}",
                amount=Money(Decimal("200.00")),
                date=today - timedelta(days=10),
                payment_method="credit_1x",
            )
            for index in range(3)
        ]

        all_sales = matched_sales + missing_sales

        matched_transactions = [
            AcquirerTransaction(
                id=f"txn-match-{index}",
                tenant_id=tenant_id,
                acquirer="cielo",
                nsu=f"MATCH{index}",
                amount=Money(Decimal("100.00")),
                transaction_date=today,
                mdr_amount=Money(Decimal("3.00")),
                net_amount=Money(Decimal("97.00")),
            )
            for index in range(5)
        ]

        unexpected_fees = [
            AcquirerTransaction(
                id=f"txn-fee-{index}",
                tenant_id=tenant_id,
                acquirer="cielo",
                nsu=f"FEE{index:04d}",
                amount=Money(Decimal("150.00")),
                transaction_date=today,
                mdr_amount=Money(Decimal("150.00")),
                net_amount=Money(Decimal("0.00")),
            )
            for index in range(2)
        ]

        all_transactions = matched_transactions + unexpected_fees

        use_case.sale_repo.find_by_date_range.return_value = all_sales
        use_case.transaction_repo.find_by_date_range.return_value = all_transactions

        result = await use_case.execute(
            tenant_id=tenant_id,
            start_date=today - timedelta(days=30),
            end_date=today,
        )

        assert result.matched_count == 5
        assert len(result.divergences) == 3
        assert result.accuracy == Decimal("0.625")
        assert use_case.divergence_repo.save.call_count == 3

    @pytest.mark.asyncio
    async def test_reconciliation_performance_target(
        self, use_case: ReconcileTransactionsUseCase
    ) -> None:
        tenant_id = "tenant-perf"
        today = date.today()

        sales = [
            Sale(
                id=f"sale-{index:04d}",
                tenant_id=tenant_id,
                nsu=f"NSU{index:07d}",
                amount=Money(Decimal(f"{100 + (index % 100)}.00")),
                date=today,
                payment_method="credit_1x",
            )
            for index in range(1000)
        ]

        transactions = [
            AcquirerTransaction(
                id=f"txn-{index:04d}",
                tenant_id=tenant_id,
                acquirer="cielo",
                nsu=f"NSU{index:07d}",
                amount=Money(Decimal(f"{100 + (index % 100)}.00")),
                transaction_date=today,
                mdr_amount=Money(Decimal("3.00")),
                net_amount=Money(Decimal(f"{97 + (index % 100)}.00")),
            )
            for index in range(1000)
        ]

        use_case.sale_repo.find_by_date_range.return_value = sales
        use_case.transaction_repo.find_by_date_range.return_value = transactions

        result = await use_case.execute(
            tenant_id=tenant_id,
            start_date=today,
            end_date=today,
        )

        assert result.matched_count == 1000
        assert result.accuracy == Decimal("1")
