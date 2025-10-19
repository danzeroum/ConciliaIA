"""Unit tests for the :mod:`ExactMatcher` strategy."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from src.application.strategies import ExactMatcher
from src.domain.entities import AcquirerTransaction, MatchType, Money, Sale


class TestExactMatcher:
    @pytest.fixture
    def matcher(self) -> ExactMatcher:
        return ExactMatcher()

    @pytest.fixture
    def sample_sale(self) -> Sale:
        return Sale(
            id="sale-001",
            tenant_id="tenant-123",
            nsu="123456789",
            amount=Money(Decimal("150.00")),
            date=date(2025, 1, 15),
            payment_method="credit_1x",
            installments=1,
        )

    @pytest.fixture
    def matching_transaction(self) -> AcquirerTransaction:
        return AcquirerTransaction(
            id="txn-001",
            tenant_id="tenant-123",
            acquirer="cielo",
            nsu="123456789",
            transaction_date=date(2025, 1, 15),
            settlement_date=date(2025, 2, 15),
            gross_amount=Money(Decimal("150.00")),
            mdr_fee=Money(Decimal("4.50")),
            net_amount=Money(Decimal("145.50")),
            installments=1,
        )

    @pytest.mark.asyncio
    async def test_exact_match_success(
        self,
        matcher: ExactMatcher,
        sample_sale: Sale,
        matching_transaction: AcquirerTransaction,
    ) -> None:
        matches, unmatched_sales, unmatched_transactions = await matcher.match(
            sales=[sample_sale],
            transactions=[matching_transaction],
        )

        assert len(matches) == 1
        assert not unmatched_sales
        assert not unmatched_transactions

        match = matches[0]
        assert match.sale_id == sample_sale.id
        assert match.transaction_id == matching_transaction.id
        assert match.match_type == MatchType.EXACT
        assert match.confidence == Decimal("1.0")

    @pytest.mark.asyncio
    async def test_no_match_when_nsu_differs(
        self,
        matcher: ExactMatcher,
        sample_sale: Sale,
        matching_transaction: AcquirerTransaction,
    ) -> None:
        mismatching_transaction = AcquirerTransaction(
            id="txn-002",
            tenant_id="tenant-123",
            acquirer="cielo",
            nsu="000000000",
            transaction_date=matching_transaction.transaction_date,
            settlement_date=matching_transaction.settlement_date,
            gross_amount=matching_transaction.gross_amount,
            mdr_fee=matching_transaction.mdr_fee,
            net_amount=matching_transaction.net_amount,
        )

        matches, unmatched_sales, unmatched_transactions = await matcher.match(
            sales=[sample_sale],
            transactions=[mismatching_transaction],
        )

        assert not matches
        assert len(unmatched_sales) == 1
        assert len(unmatched_transactions) == 1
        assert unmatched_sales[0].id == sample_sale.id

    @pytest.mark.asyncio
    async def test_no_match_when_amount_differs(
        self,
        matcher: ExactMatcher,
        sample_sale: Sale,
    ) -> None:
        transaction = AcquirerTransaction(
            id="txn-003",
            tenant_id="tenant-123",
            acquirer="cielo",
            nsu="123456789",
            transaction_date=date(2025, 1, 15),
            settlement_date=date(2025, 2, 15),
            gross_amount=Money(Decimal("150.01")),
            mdr_fee=Money(Decimal("4.50")),
            net_amount=Money(Decimal("145.51")),
        )

        matches, unmatched_sales, _ = await matcher.match(
            sales=[sample_sale],
            transactions=[transaction],
        )

        assert not matches
        assert unmatched_sales == [sample_sale]

    @pytest.mark.asyncio
    async def test_multiple_sales_and_transactions(self, matcher: ExactMatcher) -> None:
        sales = [
            Sale(
                id=f"sale-{index}",
                tenant_id="tenant-123",
                nsu=f"NSU{index:03d}",
                amount=Money(Decimal(f"{100 + index}.00")),
                date=date(2025, 1, 15),
                payment_method="credit_1x",
            )
            for index in range(3)
        ]

        transactions = [
            AcquirerTransaction(
                id=f"txn-{index}",
                tenant_id="tenant-123",
                acquirer="cielo",
                nsu=f"NSU{index:03d}",
                transaction_date=date(2025, 1, 15),
                settlement_date=date(2025, 2, 15),
                gross_amount=Money(Decimal(f"{100 + index}.00")),
                mdr_fee=Money(Decimal("3.00")),
                net_amount=Money(Decimal(f"{97 + index}.00")),
            )
            for index in range(3)
        ]

        matches, unmatched_sales, unmatched_transactions = await matcher.match(
            sales=sales,
            transactions=transactions,
        )

        assert len(matches) == 3
        assert not unmatched_sales
        assert not unmatched_transactions
        assert all(match.match_type == MatchType.EXACT for match in matches)
        assert all(match.confidence == Decimal("1.0") for match in matches)

    @pytest.mark.asyncio
    async def test_prevent_duplicate_transactions(self, matcher: ExactMatcher) -> None:
        sales = [
            Sale(
                id="sale-001",
                tenant_id="tenant-123",
                nsu="DUPLICATE",
                amount=Money(Decimal("100.00")),
                date=date(2025, 1, 10),
                payment_method="credit_1x",
            ),
            Sale(
                id="sale-002",
                tenant_id="tenant-123",
                nsu="DUPLICATE",
                amount=Money(Decimal("100.00")),
                date=date(2025, 1, 10),
                payment_method="credit_1x",
            ),
        ]

        transaction = AcquirerTransaction(
            id="txn-001",
            tenant_id="tenant-123",
            acquirer="cielo",
            nsu="DUPLICATE",
            transaction_date=date(2025, 1, 10),
            settlement_date=date(2025, 2, 10),
            gross_amount=Money(Decimal("100.00")),
            mdr_fee=Money(Decimal("3.00")),
            net_amount=Money(Decimal("97.00")),
        )

        matches, unmatched_sales, unmatched_transactions = await matcher.match(
            sales=sales,
            transactions=[transaction],
        )

        assert len(matches) == 1
        assert len(unmatched_sales) == 1
        assert not unmatched_transactions
