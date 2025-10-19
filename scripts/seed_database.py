"""Seed database with sample data for development."""

from __future__ import annotations

import asyncio
from datetime import date, timedelta
from decimal import Decimal
from uuid import uuid4

from src.domain.entities import AcquirerTransaction, Sale
from src.domain.value_objects import Acquirer, Money
from src.infrastructure.persistence.database import Database
from src.infrastructure.persistence.repositories.postgresql_sale_repository import PostgreSQLSaleRepository
from src.infrastructure.persistence.repositories.postgresql_transaction_repository import (
    PostgreSQLTransactionRepository,
)


async def seed_data() -> None:
    """Seed database with sample data."""
    database_url = "postgresql+asyncpg://btv_user:btv_password@localhost:5432/conciliaai"
    database = Database(database_url)

    async for session in database.get_session():
        sale_repo = PostgreSQLSaleRepository(session)
        transaction_repo = PostgreSQLTransactionRepository(session)

        tenant_id = str(uuid4())

        print(f"🌱 Seeding data for tenant: {tenant_id}")

        for i in range(100):
            amount = Decimal(100 + i * 10)
            sale = Sale(
                id=str(uuid4()),
                tenant_id=tenant_id,
                nsu=f"NSU{i:09d}",
                amount=Money(amount),
                date=date.today() - timedelta(days=i % 30),
                payment_method="credit_card" if i % 2 == 0 else "debit_card",
            )
            await sale_repo.save(sale)

            if i < 95:
                transaction = AcquirerTransaction(
                    id=str(uuid4()),
                    tenant_id=tenant_id,
                    acquirer=Acquirer.CIELO if i % 3 == 0 else Acquirer.REDE,
                    nsu=f"NSU{i:09d}",
                    amount=Money(amount),
                    transaction_date=date.today() - timedelta(days=i % 30),
                    mdr_amount=Money(amount * Decimal("0.025")),
                    net_amount=Money(amount * Decimal("0.975")),
                )
                await transaction_repo.save(transaction)

        print("✅ Seeded 100 sales and 95 transactions")
        await session.commit()

    await database.close()


if __name__ == "__main__":
    asyncio.run(seed_data())
