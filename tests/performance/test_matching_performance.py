"""Performance tests for matching strategies."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from statistics import mean, stdev
from time import perf_counter
from typing import List

import pytest

from src.application.services import MatchingService
from src.application.strategies import (
    ExactMatcher,
    FuzzyMatcher,
    InstallmentMatcher,
    MLMatcher,
)
from src.domain.entities import AcquirerTransaction, Sale
from src.domain.value_objects import Acquirer, Money


def generate_sales(count: int) -> List[Sale]:
    """Generate test sales."""
    today = date.today()
    base_amount = Decimal("100.00")

    return [
        Sale(
            id=f"sale-{i:06d}",
            tenant_id="tenant-perf",
            nsu=f"NSU{i:09d}",
            amount=Money(base_amount + Decimal(i)),
            date=today,
            payment_method="credit_card",
        )
        for i in range(count)
    ]


def generate_transactions(count: int) -> List[AcquirerTransaction]:
    """Generate test transactions."""
    today = date.today()
    base_amount = Decimal("100.00")

    return [
        AcquirerTransaction(
            id=f"txn-{i:06d}",
            tenant_id="tenant-perf",
            acquirer=Acquirer.CIELO,
            nsu=f"NSU{i:09d}",
            amount=Money(base_amount + Decimal(i)),
            transaction_date=today,
        )
        for i in range(count)
    ]


@pytest.mark.performance
@pytest.mark.asyncio
class TestMatchingPerformance:
    """Performance tests for matching."""

    async def test_exact_matcher_performance_100_transactions(self) -> None:
        """Test ExactMatcher with 100 transactions."""
        matcher = ExactMatcher()
        sales = generate_sales(100)
        transactions = generate_transactions(100)

        await matcher.match(sales[:10], transactions[:10])  # Warm-up

        start = perf_counter()
        matches, _, _ = await matcher.match(sales, transactions)
        elapsed_ms = (perf_counter() - start) * 1000

        print(f"\n📊 ExactMatcher (100 transactions): {elapsed_ms:.2f}ms")
        print(f"   Matches: {len(matches)}")
        print(f"   Throughput: {100 / (elapsed_ms / 1000):.0f} txn/s")

        assert elapsed_ms < 50, f"Performance degraded: {elapsed_ms:.2f}ms > 50ms"
        assert len(matches) == 100

    async def test_matching_service_cascade_performance_100_transactions(self) -> None:
        """Test full cascade with 100 transactions."""
        matching_service = MatchingService(
            exact_matcher=ExactMatcher(),
            fuzzy_matcher=FuzzyMatcher(),
            ml_matcher=MLMatcher(),
            installment_matcher=InstallmentMatcher(),
        )

        sales = generate_sales(100)
        transactions = generate_transactions(100)

        await matching_service.match_all(sales[:10], transactions[:10])  # Warm-up

        start = perf_counter()
        matches, _, _ = await matching_service.match_all(sales, transactions)
        elapsed_ms = (perf_counter() - start) * 1000

        print(f"\n📊 Cascade Matching (100 transactions): {elapsed_ms:.2f}ms")
        print(f"   Matches: {len(matches)}")
        print(f"   Throughput: {100 / (elapsed_ms / 1000):.0f} txn/s")

        assert elapsed_ms < 100, f"Performance degraded: {elapsed_ms:.2f}ms > 100ms"

    async def test_matching_service_cascade_performance_1000_transactions(self) -> None:
        """Test full cascade with 1000 transactions."""
        matching_service = MatchingService(
            exact_matcher=ExactMatcher(),
            fuzzy_matcher=FuzzyMatcher(),
            ml_matcher=MLMatcher(),
            installment_matcher=InstallmentMatcher(),
        )

        sales = generate_sales(1000)
        transactions = generate_transactions(1000)

        start = perf_counter()
        matches, _, _ = await matching_service.match_all(sales, transactions)
        elapsed_ms = (perf_counter() - start) * 1000

        print(f"\n📊 Cascade Matching (1000 transactions): {elapsed_ms:.2f}ms")
        print(f"   Matches: {len(matches)}")
        print(f"   Throughput: {1000 / (elapsed_ms / 1000):.0f} txn/s")

        assert elapsed_ms < 500, f"Performance degraded: {elapsed_ms:.2f}ms > 500ms"

    async def test_matching_latency_percentiles(self) -> None:
        """Test matching latency percentiles (P50, P95, P99)."""
        matcher = ExactMatcher()
        latencies: list[float] = []

        for _ in range(100):
            sales = generate_sales(100)
            transactions = generate_transactions(100)

            start = perf_counter()
            await matcher.match(sales, transactions)
            elapsed_ms = (perf_counter() - start) * 1000

            latencies.append(elapsed_ms)

        latencies.sort()
        p50 = latencies[49]
        p95 = latencies[94]
        p99 = latencies[98]

        print("\n📊 Latency Percentiles (100 txn, 100 iterations):")
        print(f"   P50: {p50:.2f}ms")
        print(f"   P95: {p95:.2f}ms")
        print(f"   P99: {p99:.2f}ms")
        print(f"   Mean: {mean(latencies):.2f}ms")
        print(f"   StdDev: {stdev(latencies):.2f}ms")

        assert p50 < 30, f"P50 latency too high: {p50:.2f}ms"
        assert p95 < 50, f"P95 latency too high: {p95:.2f}ms"
        assert p99 < 80, f"P99 latency too high: {p99:.2f}ms"
