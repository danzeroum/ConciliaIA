"""Seed database with sample data for development (BuildToValue v7 / ConciliaAI)."""

from __future__ import annotations

import asyncio
import os
import sys
from datetime import date, timedelta
from decimal import Decimal
from uuid import uuid4

import structlog
from sqlalchemy import text

# --- Ajuste de path do projeto ---
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# --- FIM ---

from src.domain.entities import AcquirerTransaction, Sale
from src.domain.entities.tenant import TenantTier
from src.domain.value_objects import Acquirer, Money
from src.infrastructure.persistence.models import TenantModel
from src.infrastructure.persistence.database import Database
from src.infrastructure.persistence.repositories.postgresql_sale_repository import PostgreSQLSaleRepository
from src.infrastructure.persistence.repositories.postgresql_transaction_repository import (
    PostgreSQLTransactionRepository,
)

logger = structlog.get_logger(__name__)

# URL atualizada conforme docker-compose
DEFAULT_DB_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://btv_user:btv_password@postgres:5432/buildtovalue",
)


async def check_tables_exist(engine) -> None:
    """Verifica se a tabela 'tenants' existe antes de semear os dados."""
    async with engine.connect() as conn:
        result = await conn.execute(
            text(
                """
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_name = 'tenants'
                """
            )
        )
        if not result.fetchone():
            raise RuntimeError(
                "❌ ERROR: Table 'tenants' does not exist!\n"
                "Run migrations first:\n"
                "docker exec conciliaai-backend alembic upgrade head"
            )
    logger.info("table_check_passed", tables="tenants exists")


async def seed_data() -> None:
    """Insere dados de exemplo para ambiente de desenvolvimento."""
    database_url = DEFAULT_DB_URL
    database = Database(database_url)
    engine = database.engine

    logger.info("database_initialized", url=database_url.replace("btv_password", "***"))

    # Garante que as tabelas existem antes de popular dados
    await check_tables_exist(engine)

    async for session in database.get_session():
        sale_repo = PostgreSQLSaleRepository(session)
        transaction_repo = PostgreSQLTransactionRepository(session)

        tenant_id = str(uuid4())

        # --- Cria TenantModel (ORM) ---
        tenant_model = TenantModel(
            id=tenant_id,
            org_name="Mariana - E-commerce Owner",
            cnpj="99999999000100",
            tier=TenantTier.ALPHA.value,
            active=True,
        )
        session.add(tenant_model)
        await session.flush()  # Garante persistência antes de uso

        logger.info("tenant_created", tenant_id=tenant_id, org="Mariana - E-commerce Owner")

        # --- Seed de vendas e transações ---
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
                    transaction_time=time(14, 30 + (i % 30), 0),
                    mdr_amount=Money(amount * Decimal("0.025")),
                    net_amount=Money(amount * Decimal("0.975")),
                )
                await transaction_repo.save(transaction)

        logger.info("seed_completed", sales=100, transactions=95, tenant_id=tenant_id)
        print("✅ Seeded 100 sales and 95 transactions for tenant:", tenant_id)

    await database.close()
    logger.info("database_connection_closed")


if __name__ == "__main__":
    try:
        asyncio.run(seed_data())
        print("🎉 Database seeding completed successfully.")
    except Exception as e:
        logger.error("seed_failed", error=str(e))
        print(f"❌ Seed failed: {e}")
        sys.exit(1)
