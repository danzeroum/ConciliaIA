"""Integration tests for PostgreSQL repositories."""

from datetime import date, timedelta
from decimal import Decimal
from uuid import uuid4

import pytest

from src.domain.entities import (
    Divergence,
    DivergenceStatus,
    DivergenceType,
    MatchType,
    ReconciliationMatch,
    Sale,
    Severity,
)
from src.domain.value_objects import Money
from src.infrastructure.persistence.repositories.postgresql_divergence_repository import (
    PostgreSQLDivergenceRepository,
)
from src.infrastructure.persistence.repositories.postgresql_match_repository import (
    PostgreSQLMatchRepository,
)
from src.infrastructure.persistence.repositories.postgresql_sale_repository import (
    PostgreSQLSaleRepository,
)


@pytest.mark.integration
@pytest.mark.asyncio
class TestPostgreSQLSaleRepository:
    """Test PostgreSQL Sale Repository."""

    async def test_save_and_find_sale(self, db_session):
        """Test saving and retrieving a sale."""
        async with db_session as session:
            repo = PostgreSQLSaleRepository(session)

            sale = Sale(
                id=str(uuid4()),
                tenant_id=str(uuid4()),
                nsu="123456789",
                amount=Money(Decimal("100.00")),
                date=date.today(),
                payment_method="credit_card",
            )

            await repo.save(sale)

            found = await repo.find_by_id(sale.tenant_id, sale.id)

            assert found is not None
            assert found.id == sale.id
            assert found.nsu == sale.nsu
            assert found.amount.amount == sale.amount.amount

    async def test_find_by_date_range(self, db_session):
        """Test finding sales by date range."""
        async with db_session as session:
            repo = PostgreSQLSaleRepository(session)
            tenant_id = str(uuid4())

            for i in range(3):
                sale = Sale(
                    id=str(uuid4()),
                    tenant_id=tenant_id,
                    nsu=f"NSU{i:09d}",
                    amount=Money(Decimal(f"{100 + i}.00")),
                    date=date.today() - timedelta(days=i),
                    payment_method="credit_card",
                )
                await repo.save(sale)

            start_date = date.today() - timedelta(days=2)
            end_date = date.today()

            sales = await repo.find_by_date_range(tenant_id, start_date, end_date)

            assert len(sales) == 3
            assert all(s.tenant_id == tenant_id for s in sales)

    async def test_find_unmatched_sales(self, db_session):
        """Test finding unmatched sales."""
        async with db_session as session:
            repo = PostgreSQLSaleRepository(session)
            tenant_id = str(uuid4())

            sale = Sale(
                id=str(uuid4()),
                tenant_id=tenant_id,
                nsu="999999999",
                amount=Money(Decimal("500.00")),
                date=date.today(),
                payment_method="credit_card",
            )
            await repo.save(sale)

            unmatched = await repo.find_unmatched(tenant_id)

            assert len(unmatched) >= 1
            assert any(s.id == sale.id for s in unmatched)


@pytest.mark.integration
@pytest.mark.asyncio
class TestPostgreSQLMatchRepository:
    """Test PostgreSQL Match Repository."""

    async def test_save_and_find_match(self, db_session):
        """Test saving and retrieving a match."""
        async with db_session as session:
            repo = PostgreSQLMatchRepository(session)

            match = ReconciliationMatch(
                id=str(uuid4()),
                tenant_id=str(uuid4()),
                sale_id=str(uuid4()),
                transaction_id=str(uuid4()),
                match_type=MatchType.EXACT,
                confidence=Decimal("1.00"),
            )

            await repo.save(match)

            found = await repo.find_by_id(match.tenant_id, match.id)

            assert found is not None
            assert found.id == match.id
            assert found.confidence == Decimal("1.00")
            assert found.validated is True

    async def test_find_requiring_review(self, db_session):
        """Test finding matches requiring review."""
        async with db_session as session:
            repo = PostgreSQLMatchRepository(session)
            tenant_id = str(uuid4())

            match = ReconciliationMatch(
                id=str(uuid4()),
                tenant_id=tenant_id,
                sale_id=str(uuid4()),
                transaction_id=str(uuid4()),
                match_type=MatchType.ML_PREDICTED,
                confidence=Decimal("0.85"),
            )
            await repo.save(match)

            requiring_review = await repo.find_requiring_review(tenant_id)

            assert len(requiring_review) >= 1
            assert any(m.id == match.id for m in requiring_review)
            assert all(m.confidence < Decimal("0.95") for m in requiring_review)


@pytest.mark.integration
@pytest.mark.asyncio
class TestPostgreSQLDivergenceRepository:
    """Test PostgreSQL Divergence Repository."""

    async def test_save_and_find_divergence(self, db_session):
        """Test saving and retrieving a divergence."""
        async with db_session as session:
            repo = PostgreSQLDivergenceRepository(session)

            divergence = Divergence(
                id=str(uuid4()),
                tenant_id=str(uuid4()),
                divergence_type=DivergenceType.MISSING_TRANSACTION,
                severity=Severity.CRITICAL,
                expected_value=Money(Decimal("1000.00")),
                actual_value=Money(Decimal("0.00")),
                suggested_action="Urgente: Contestar perda",
            )

            await repo.save(divergence)

            found = await repo.find_by_id(divergence.tenant_id, divergence.id)

            assert found is not None
            assert found.id == divergence.id
            assert found.severity == Severity.CRITICAL

    async def test_find_critical_open(self, db_session):
        """Test finding critical open divergences."""
        async with db_session as session:
            repo = PostgreSQLDivergenceRepository(session)
            tenant_id = str(uuid4())

            divergence = Divergence(
                id=str(uuid4()),
                tenant_id=tenant_id,
                divergence_type=DivergenceType.MDR_VARIANCE,
                severity=Severity.CRITICAL,
                expected_value=Money(Decimal("100.00")),
                actual_value=Money(Decimal("120.00")),
                suggested_action="Contestar cobrança indevida",
                status=DivergenceStatus.OPEN,
            )
            await repo.save(divergence)

            critical = await repo.find_critical_open(tenant_id)

            assert len(critical) >= 1
            assert any(d.id == divergence.id for d in critical)
            assert all(d.severity == Severity.CRITICAL for d in critical)
