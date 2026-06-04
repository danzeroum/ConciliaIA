"""End-to-end tests for complete reconciliation flow."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from uuid import uuid4

import pytest

from src.application.services import AnomalyDetectionService, MatchingService
from src.application.strategies import ExactMatcher, FuzzyMatcher, InstallmentMatcher, MLMatcher
from src.application.use_cases.reconcile_transactions import ReconcileTransactionsUseCase
from src.domain.entities import AcquirerTransaction, Sale
from src.domain.value_objects import Acquirer, Money
from src.infrastructure.persistence.repositories.postgresql_divergence_repository import (
    PostgreSQLDivergenceRepository,
)
from src.infrastructure.persistence.repositories.postgresql_match_repository import (
    PostgreSQLMatchRepository,
)
from src.infrastructure.persistence.repositories.postgresql_sale_repository import (
    PostgreSQLSaleRepository,
)
from src.infrastructure.persistence.repositories.postgresql_transaction_repository import (
    PostgreSQLTransactionRepository,
)


@pytest.mark.e2e
@pytest.mark.asyncio
class TestReconciliationFlowE2E:
    """End-to-end reconciliation flow tests."""

    async def test_complete_reconciliation_flow(self, db_session) -> None:
        """Test complete reconciliation flow from ingestion to reporting."""
        tenant_id = str(uuid4())

        sale_repo = PostgreSQLSaleRepository(db_session)
        transaction_repo = PostgreSQLTransactionRepository(db_session)
        match_repo = PostgreSQLMatchRepository(db_session)
        divergence_repo = PostgreSQLDivergenceRepository(db_session)

        sales_data = [
            {"nsu": "NSU001", "amount": Decimal("100.00")},
            {"nsu": "NSU002", "amount": Decimal("200.00")},
            {"nsu": "NSU003", "amount": Decimal("300.00")},
            {"nsu": "NSU004", "amount": Decimal("400.00")},
        ]

        for item in sales_data:
            sale = Sale(
                id=str(uuid4()),
                tenant_id=tenant_id,
                nsu=item["nsu"],
                amount=Money(item["amount"]),
                date=date.today(),
                payment_method="credit_card",
            )
            await sale_repo.save(sale)

        transactions_data = [
            {"nsu": "NSU001", "amount": Decimal("100.00")},
            {"nsu": "NSU002", "amount": Decimal("200.30")},
            {"nsu": "NSU003", "amount": Decimal("300.00")},
            {"nsu": "NSU999", "amount": Decimal("999.00")},
        ]

        for item in transactions_data:
            transaction = AcquirerTransaction(
                id=str(uuid4()),
                tenant_id=tenant_id,
                acquirer=Acquirer.CIELO,
                nsu=item["nsu"],
                amount=Money(item["amount"]),
                transaction_date=date.today(),
            )
            await transaction_repo.save(transaction)

        await db_session.commit()

        matching_service = MatchingService(
            exact_matcher=ExactMatcher(),
            fuzzy_matcher=FuzzyMatcher(),
            ml_matcher=MLMatcher(),
            installment_matcher=InstallmentMatcher(),
        )
        anomaly_service = AnomalyDetectionService()

        use_case = ReconcileTransactionsUseCase(
            sale_repo=sale_repo,
            transaction_repo=transaction_repo,
            match_repo=match_repo,
            divergence_repo=divergence_repo,
            matching_service=matching_service,
            anomaly_service=anomaly_service,
        )

        result = await use_case.execute(
            tenant_id=tenant_id,
            start_date=date.today(),
            end_date=date.today(),
        )

        assert result.total_sales == 4
        assert result.total_transactions == 4
        assert result.matched_count == 3
        assert result.unmatched_sales_count == 1
        assert result.accuracy >= Decimal("0.75")
        assert len(result.divergences) >= 1

        missing_divergences = [
            divergence
            for divergence in result.divergences
            if divergence.divergence_type.value == "missing_transaction"
        ]
        assert len(missing_divergences) >= 1

        print("\n📊 E2E Reconciliation Results:")
        print(f"   Total Sales: {result.total_sales}")
        print(f"   Total Transactions: {result.total_transactions}")
        print(f"   Matches: {result.matched_count}")
        print(f"   Accuracy: {float(result.accuracy):.2%}")
        print(f"   Divergences: {len(result.divergences)}")
