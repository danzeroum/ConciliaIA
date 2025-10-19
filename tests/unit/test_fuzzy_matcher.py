"""Unit tests for the :mod:`FuzzyMatcher` strategy."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from src.application.strategies import FuzzyMatcher
from src.domain.entities import AcquirerTransaction, MatchType, Money, Sale


class TestFuzzyMatcher:
    @pytest.fixture
    def matcher(self) -> FuzzyMatcher:
        return FuzzyMatcher()

    @pytest.mark.asyncio
    async def test_fuzzy_amount_within_tolerance(self, matcher: FuzzyMatcher) -> None:
        sale = Sale(
            id="sale-001",
            tenant_id="tenant-123",
            nsu="NSU123",
            amount=Money(Decimal("150.00")),
            date=date(2025, 1, 15),
            payment_method="credit_1x",
        )

        transaction = AcquirerTransaction(
            id="txn-001",
            tenant_id="tenant-123",
            acquirer="cielo",
            nsu="NSU123",
            transaction_date=date(2025, 1, 15),
            settlement_date=date(2025, 2, 15),
            gross_amount=Money(Decimal("149.75")),
            mdr_fee=Money(Decimal("4.49")),
            net_amount=Money(Decimal("145.26")),
        )

        matches, _, _ = await matcher.match(sales=[sale], transactions=[transaction])

        assert len(matches) == 1
        match = matches[0]
        assert match.match_type == MatchType.FUZZY_AMOUNT
        assert Decimal("0.90") <= match.confidence <= Decimal("0.95")

    @pytest.mark.asyncio
    async def test_fuzzy_amount_exceeds_tolerance(self, matcher: FuzzyMatcher) -> None:
        sale = Sale(
            id="sale-001",
            tenant_id="tenant-123",
            nsu="NSU123",
            amount=Money(Decimal("150.00")),
            date=date(2025, 1, 15),
            payment_method="credit_1x",
        )

        transaction = AcquirerTransaction(
            id="txn-001",
            tenant_id="tenant-123",
            acquirer="cielo",
            nsu="NSU123",
            transaction_date=date(2025, 1, 15),
            settlement_date=date(2025, 2, 15),
            gross_amount=Money(Decimal("149.40")),
            mdr_fee=Money(Decimal("4.48")),
            net_amount=Money(Decimal("144.92")),
        )

        matches, unmatched_sales, _ = await matcher.match(
            sales=[sale], transactions=[transaction]
        )

        assert not matches
        assert unmatched_sales == [sale]

    @pytest.mark.asyncio
    async def test_fuzzy_date_one_day_difference(self, matcher: FuzzyMatcher) -> None:
        sale = Sale(
            id="sale-001",
            tenant_id="tenant-123",
            nsu="NSU123",
            amount=Money(Decimal("150.00")),
            date=date(2025, 1, 15),
            payment_method="credit_1x",
        )

        transaction = AcquirerTransaction(
            id="txn-001",
            tenant_id="tenant-123",
            acquirer="cielo",
            nsu="NSU123",
            transaction_date=date(2025, 1, 16),
            settlement_date=date(2025, 2, 16),
            gross_amount=Money(Decimal("150.00")),
            mdr_fee=Money(Decimal("4.50")),
            net_amount=Money(Decimal("145.50")),
        )

        matches, _, _ = await matcher.match(sales=[sale], transactions=[transaction])

        assert len(matches) == 1
        match = matches[0]
        assert match.match_type == MatchType.FUZZY_DATE
        assert match.confidence == Decimal("0.90")

    @pytest.mark.asyncio
    async def test_fuzzy_date_exceeds_tolerance(self, matcher: FuzzyMatcher) -> None:
        sale = Sale(
            id="sale-001",
            tenant_id="tenant-123",
            nsu="NSU123",
            amount=Money(Decimal("150.00")),
            date=date(2025, 1, 15),
            payment_method="credit_1x",
        )

        transaction = AcquirerTransaction(
            id="txn-001",
            tenant_id="tenant-123",
            acquirer="cielo",
            nsu="NSU123",
            transaction_date=date(2025, 1, 17),
            settlement_date=date(2025, 2, 17),
            gross_amount=Money(Decimal("150.00")),
            mdr_fee=Money(Decimal("4.50")),
            net_amount=Money(Decimal("145.50")),
        )

        matches, unmatched_sales, _ = await matcher.match(
            sales=[sale], transactions=[transaction]
        )

        assert not matches
        assert unmatched_sales == [sale]

    @pytest.mark.asyncio
    async def test_confidence_calculation_accuracy(self, matcher: FuzzyMatcher) -> None:
        diffs = [
            (Decimal("0.10"), Decimal("0.93")),
            (Decimal("0.25"), Decimal("0.90")),
            (Decimal("0.50"), Decimal("0.85")),
        ]

        for diff, minimum_confidence in diffs:
            sale = Sale(
                id="sale-001",
                tenant_id="tenant-123",
                nsu="NSU123",
                amount=Money(Decimal("100.00")),
                date=date(2025, 1, 15),
                payment_method="credit_1x",
            )

            transaction = AcquirerTransaction(
                id="txn-001",
                tenant_id="tenant-123",
                acquirer="cielo",
                nsu="NSU123",
                transaction_date=date(2025, 1, 15),
                settlement_date=date(2025, 2, 15),
                gross_amount=Money(Decimal("100.00") - diff),
                mdr_fee=Money(Decimal("3.00")),
                net_amount=Money(Decimal("97.00") - diff),
            )

            matches, _, _ = await matcher.match(
                sales=[sale], transactions=[transaction]
            )

            assert len(matches) == 1
            assert matches[0].confidence >= minimum_confidence
