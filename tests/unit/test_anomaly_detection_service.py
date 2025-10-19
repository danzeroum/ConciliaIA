"""Unit tests for the :mod:`AnomalyDetectionService`."""

from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal

import pytest

from src.application.services import AnomalyDetectionService
from src.domain.entities import AcquirerTransaction, DivergenceType, Sale, Severity
from src.domain.value_objects import Money


class TestAnomalyDetectionService:
    @pytest.fixture
    def service(self) -> AnomalyDetectionService:
        return AnomalyDetectionService()

    @pytest.mark.asyncio
    async def test_missing_transaction_medium_severity(
        self, service: AnomalyDetectionService
    ) -> None:
        sale = Sale(
            id="sale-001",
            tenant_id="tenant-123",
            nsu="NSU123",
            amount=Money(Decimal("150.00")),
            date=date.today() - timedelta(days=8),
            payment_method="credit_1x",
        )

        divergences = await service.detect_all_anomalies(
            tenant_id="tenant-123",
            unmatched_sales=[sale],
            unmatched_transactions=[],
            matches=[],
        )

        assert len(divergences) == 1
        divergence = divergences[0]
        assert divergence.divergence_type is DivergenceType.MISSING_TRANSACTION
        assert divergence.severity is Severity.MEDIUM
        assert divergence.expected_value == sale.amount

    @pytest.mark.asyncio
    async def test_missing_transaction_high_severity(
        self, service: AnomalyDetectionService
    ) -> None:
        sale = Sale(
            id="sale-002",
            tenant_id="tenant-123",
            nsu="NSU456",
            amount=Money(Decimal("500.00")),
            date=date.today() - timedelta(days=35),
            payment_method="credit_1x",
        )

        divergences = await service.detect_all_anomalies(
            tenant_id="tenant-123",
            unmatched_sales=[sale],
            unmatched_transactions=[],
            matches=[],
        )

        assert len(divergences) == 1
        assert divergences[0].severity is Severity.HIGH

    @pytest.mark.asyncio
    async def test_missing_transaction_critical_severity(
        self, service: AnomalyDetectionService
    ) -> None:
        sale = Sale(
            id="sale-003",
            tenant_id="tenant-123",
            nsu="NSU789",
            amount=Money(Decimal("1000.00")),
            date=date.today() - timedelta(days=95),
            payment_method="credit_1x",
        )

        divergences = await service.detect_all_anomalies(
            tenant_id="tenant-123",
            unmatched_sales=[sale],
            unmatched_transactions=[],
            matches=[],
        )

        assert len(divergences) == 1
        assert divergences[0].severity is Severity.CRITICAL

    @pytest.mark.asyncio
    async def test_no_divergence_within_seven_days(
        self, service: AnomalyDetectionService
    ) -> None:
        sale = Sale(
            id="sale-004",
            tenant_id="tenant-123",
            nsu="NSU999",
            amount=Money(Decimal("100.00")),
            date=date.today() - timedelta(days=5),
            payment_method="debit",
        )

        divergences = await service.detect_all_anomalies(
            tenant_id="tenant-123",
            unmatched_sales=[sale],
            unmatched_transactions=[],
            matches=[],
        )

        assert not divergences

    @pytest.mark.asyncio
    async def test_duplicate_transaction_detection(
        self, service: AnomalyDetectionService
    ) -> None:
        transaction1 = AcquirerTransaction(
            id="txn-999",
            tenant_id="tenant-123",
            acquirer="cielo",
            nsu="DUPL001",
            amount=Money(Decimal("150.00")),
            transaction_date=date.today(),
            mdr_amount=Money(Decimal("4.50")),
            net_amount=Money(Decimal("145.50")),
        )
        transaction2 = AcquirerTransaction(
            id="txn-1000",
            tenant_id="tenant-123",
            acquirer="cielo",
            nsu="DUPL001",
            amount=Money(Decimal("150.00")),
            transaction_date=date.today(),
            mdr_amount=Money(Decimal("4.50")),
            net_amount=Money(Decimal("145.50")),
        )

        divergences = await service.detect_all_anomalies(
            tenant_id="tenant-123",
            unmatched_sales=[],
            unmatched_transactions=[transaction1, transaction2],
            matches=[],
        )

        assert len(divergences) == 1
        divergence = divergences[0]
        assert divergence.divergence_type is DivergenceType.DUPLICATE_TRANSACTION
        assert divergence.severity is Severity.HIGH
