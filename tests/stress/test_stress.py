"""Stress tests to find system limits."""

from __future__ import annotations

import asyncio
from time import perf_counter

import pytest

from src.application.services import MatchingService
from src.application.strategies import ExactMatcher, FuzzyMatcher, InstallmentMatcher, MLMatcher
from tests.performance.test_matching_performance import generate_sales, generate_transactions


@pytest.mark.stress
@pytest.mark.asyncio
class TestStress:
    """Stress tests to find breaking points."""

    async def test_matching_with_10k_transactions(self) -> None:
        """Test matching with 10,000 transactions."""
        matching_service = MatchingService(
            exact_matcher=ExactMatcher(),
            fuzzy_matcher=FuzzyMatcher(),
            ml_matcher=MLMatcher(),
            installment_matcher=InstallmentMatcher(),
        )

        sales = generate_sales(10000)
        transactions = generate_transactions(10000)

        start = perf_counter()
        matches, unmatched_sales, unmatched_transactions = await matching_service.match_all(
            sales, transactions
        )
        elapsed_sec = perf_counter() - start

        print("\n📊 Stress Test - 10K Transactions:")
        print(f"   Time: {elapsed_sec:.2f}s")
        print(f"   Matches: {len(matches)}")
        print(f"   Throughput: {10000 / elapsed_sec:.0f} txn/s")

        assert elapsed_sec < 10, f"Too slow: {elapsed_sec:.2f}s > 10s"
        assert len(matches) > 9000
        assert len(unmatched_sales) + len(unmatched_transactions) < 1000

    async def test_concurrent_matching_requests(self) -> None:
        """Test multiple concurrent matching operations."""
        matching_service = MatchingService(
            exact_matcher=ExactMatcher(),
            fuzzy_matcher=FuzzyMatcher(),
            ml_matcher=MLMatcher(),
            installment_matcher=InstallmentMatcher(),
        )

        async def match_batch() -> tuple:
            sales = generate_sales(100)
            transactions = generate_transactions(100)
            return await matching_service.match_all(sales, transactions)

        start = perf_counter()

        tasks = [match_batch() for _ in range(50)]
        results = await asyncio.gather(*tasks)

        elapsed_sec = perf_counter() - start
        total_matches = sum(len(result[0]) for result in results)

        print("\n📊 Concurrent Stress Test:")
        print("   Concurrent Operations: 50")
        print("   Total Transactions: 5000")
        print(f"   Total Time: {elapsed_sec:.2f}s")
        print(f"   Total Matches: {total_matches}")
        print(f"   Throughput: {5000 / elapsed_sec:.0f} txn/s")

        assert elapsed_sec < 30, f"Concurrent operations too slow: {elapsed_sec:.2f}s"
        assert total_matches > 4500
