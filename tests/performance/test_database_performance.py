"""Database query performance tests."""

from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal
from time import perf_counter
from uuid import uuid4

import pytest

from src.domain.entities import Sale
from src.domain.value_objects import Money
from src.infrastructure.persistence.repositories.postgresql_sale_repository import (
    PostgreSQLSaleRepository,
)


@pytest.mark.performance
@pytest.mark.asyncio
class TestDatabasePerformance:
    """Performance tests for database operations."""

    async def test_batch_insert_performance(self, db_session) -> None:
        """Test batch insert performance."""
        repo = PostgreSQLSaleRepository(db_session)
        tenant_id = str(uuid4())

        sales = [
            Sale(
                id=str(uuid4()),
                tenant_id=tenant_id,
                nsu=f"NSU{i:09d}",
                amount=Money(Decimal("100.00") + Decimal(i)),
                date=date.today(),
                payment_method="credit_card",
            )
            for i in range(1000)
        ]

        start = perf_counter()

        for sale in sales:
            await repo.save(sale)

        await db_session.commit()

        elapsed_ms = (perf_counter() - start) * 1000
        throughput = 1000 / (elapsed_ms / 1000)

        print("\n📊 Batch Insert (1000 records):")
        print(f"   Time: {elapsed_ms:.2f}ms")
        print(f"   Throughput: {throughput:.0f} records/s")

        assert throughput > 500, f"Insert throughput too low: {throughput:.0f} records/s"

    async def test_date_range_query_performance(self, db_session) -> None:
        """Test date range query performance."""
        repo = PostgreSQLSaleRepository(db_session)
        tenant_id = str(uuid4())

        for i in range(100):
            sale = Sale(
                id=str(uuid4()),
                tenant_id=tenant_id,
                nsu=f"NSU{i:09d}",
                amount=Money(Decimal("100.00") + Decimal(i)),
                date=date.today() - timedelta(days=i % 30),
                payment_method="credit_card",
            )
            await repo.save(sale)

        await db_session.commit()

        start = perf_counter()

        sales = await repo.find_by_date_range(
            tenant_id=tenant_id,
            start_date=date.today() - timedelta(days=30),
            end_date=date.today(),
        )

        elapsed_ms = (perf_counter() - start) * 1000

        print("\n📊 Date Range Query:")
        print(f"   Records Found: {len(sales)}")
        print(f"   Query Time: {elapsed_ms:.2f}ms")

        assert elapsed_ms < 50, f"Query too slow: {elapsed_ms:.2f}ms > 50ms"
        assert len(sales) > 0
