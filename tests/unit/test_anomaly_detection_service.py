"""Unit tests for the :mod:`AnomalyDetectionService`."""

from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal

import pytest

from src.application.services import AnomalyDetectionService
from src.domain.entities import AcquirerTransaction, Money, Sale, Severity


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

        divergences = await service.detect_anomalies(
            tenant_id="tenant-123",
            unmatched_sales=[sale],
            unmatched_transactions=[],
        )

        assert len(divergences) == 1
        divergence = divergences[0]
        assert divergence.type == "missing_transaction"
        assert divergence.severity == Severity.MEDIUM
        assert divergence.sale_id == sale.id
        assert divergence.amount_at_risk == sale.amount

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

        divergences = await service.detect_anomalies(
            tenant_id="tenant-123",
            unmatched_sales=[sale],
            unmatched_transactions=[],
        )

        assert len(divergences) == 1
        assert divergences[0].severity == Severity.HIGH

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

        divergences = await service.detect_anomalies(
            tenant_id="tenant-123",
            unmatched_sales=[sale],
            unmatched_transactions=[],
        )

        assert len(divergences) == 1
        assert divergences[0].severity == Severity.CRITICAL

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

        divergences = await service.detect_anomalies(
            tenant_id="tenant-123",
            unmatched_sales=[sale],
            unmatched_transactions=[],
        )

        assert not divergences

    @pytest.mark.asyncio
    async def test_unexpected_fee_detection(
        self, service: AnomalyDetectionService
    ) -> None:
        transaction = AcquirerTransaction(
            id="txn-999",
            tenant_id="tenant-123",
            acquirer="cielo",
            nsu="FEE001",
            transaction_date=date.today(),
            settlement_date=date.today() + timedelta(days=30),
            gross_amount=Money(Decimal("150.00")),
            mdr_fee=Money(Decimal("150.00")),
            net_amount=Money(Decimal("0.00")),
        )

        divergences = await service.detect_anomalies(
            tenant_id="tenant-123",
            unmatched_sales=[],
            unmatched_transactions=[transaction],
        )

        assert len(divergences) == 1
        divergence = divergences[0]
        assert divergence.type == "unexpected_fee"
        assert divergence.transaction_id == transaction.id
        assert divergence.amount_at_risk == transaction.mdr_fee
