"""API endpoint performance tests."""

from __future__ import annotations

import asyncio
from statistics import mean
from time import perf_counter

import pytest
from httpx import AsyncClient

from src.api.main import app


@pytest.mark.performance
@pytest.mark.asyncio
class TestAPIPerformance:
    """Performance tests for API endpoints."""

    async def test_health_endpoint_latency(self) -> None:
        """Test health endpoint latency."""
        latencies: list[float] = []

        async with AsyncClient(app=app, base_url="http://test") as client:
            for _ in range(10):
                await client.get("/health")  # Warm-up

            for _ in range(100):
                start = perf_counter()
                response = await client.get("/health")
                elapsed_ms = (perf_counter() - start) * 1000

                assert response.status_code == 200
                latencies.append(elapsed_ms)

        latencies.sort()
        p50 = latencies[49]
        p95 = latencies[94]
        p99 = latencies[98]

        print("\n📊 Health Endpoint Latency:")
        print(f"   P50: {p50:.2f}ms")
        print(f"   P95: {p95:.2f}ms")
        print(f"   P99: {p99:.2f}ms")
        print(f"   Mean: {mean(latencies):.2f}ms")

        assert p50 < 5, f"P50 too high: {p50:.2f}ms"
        assert p95 < 10, f"P95 too high: {p95:.2f}ms"
        assert p99 < 20, f"P99 too high: {p99:.2f}ms"

    async def test_concurrent_requests_throughput(self) -> None:
        """Test concurrent request handling."""
        num_requests = 100
        concurrent_clients = 10

        async def make_requests(client: AsyncClient, count: int) -> None:
            for _ in range(count):
                response = await client.get("/health")
                assert response.status_code == 200

        start = perf_counter()

        async with AsyncClient(app=app, base_url="http://test") as client:
            tasks = [
                make_requests(client, num_requests // concurrent_clients)
                for _ in range(concurrent_clients)
            ]
            await asyncio.gather(*tasks)

        elapsed_sec = perf_counter() - start
        throughput = num_requests / elapsed_sec

        print("\n📊 Concurrent Requests:")
        print(f"   Total Requests: {num_requests}")
        print(f"   Concurrent Clients: {concurrent_clients}")
        print(f"   Total Time: {elapsed_sec:.2f}s")
        print(f"   Throughput: {throughput:.0f} req/s")

        assert throughput > 500, f"Throughput too low: {throughput:.0f} req/s < 500 req/s"
