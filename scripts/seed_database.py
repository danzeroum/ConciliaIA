"""Seed database with sample data for development (BuildToValue v7 / ConciliaAI).

The script is **idempotent**: running it repeatedly will not duplicate the demo
tenant, its sales/transactions or the test user. It also provisions the
``test@example.com`` login used by the frontend, so a single ``seed_database``
run is enough to obtain a working environment with real data.
"""

from __future__ import annotations

import asyncio
import json
import os
import sys
from datetime import date, time, timedelta
from decimal import Decimal
from uuid import uuid4

import structlog
from sqlalchemy import select, text

# --- Ajuste de path do projeto ---
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# --- FIM ---

from src.domain.entities import AcquirerTransaction, Sale
from src.domain.entities.tenant import TenantTier
from src.domain.value_objects import Acquirer, Money
from src.infrastructure.persistence.models import TenantModel, UserModel
from src.infrastructure.persistence.database import Database
from src.infrastructure.persistence.repositories.postgresql_sale_repository import PostgreSQLSaleRepository
from src.infrastructure.persistence.repositories.postgresql_transaction_repository import (
    PostgreSQLTransactionRepository,
)
from src.infrastructure.security import PasswordHasher

logger = structlog.get_logger(__name__)

# URL atualizada conforme docker-compose
DEFAULT_DB_URL = os.getenv("DATABASE_URL")
if not DEFAULT_DB_URL:
    raise RuntimeError("DATABASE_URL environment variable is required")

# Marcadores estáveis usados para garantir idempotência do seed.
DEMO_TENANT_CNPJ = "99999999000100"
DEMO_TENANT_NAME = "Mariana - E-commerce Owner"
TEST_USER_EMAIL = os.getenv("SEED_TEST_USER_EMAIL", "test@example.com")
TEST_USER_PASSWORD = os.getenv("SEED_TEST_USER_PASSWORD", "SecurePassword123!")


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


async def _get_or_create_tenant(session) -> tuple[str, bool]:
    """Return the demo tenant id, creating it if necessary.

    Returns a tuple ``(tenant_id, created)`` where ``created`` indicates whether
    the tenant (and therefore its sample sales/transactions) was just created.
    """
    existing = await session.execute(
        select(TenantModel).where(TenantModel.cnpj == DEMO_TENANT_CNPJ)
    )
    tenant = existing.scalar_one_or_none()
    if tenant is not None:
        logger.info("tenant_exists", tenant_id=str(tenant.id))
        return str(tenant.id), False

    tenant_id = str(uuid4())
    tenant = TenantModel(
        id=tenant_id,
        org_name=DEMO_TENANT_NAME,
        cnpj=DEMO_TENANT_CNPJ,
        tier=TenantTier.ALPHA.value,
        active=True,
    )
    session.add(tenant)
    await session.flush()
    logger.info("tenant_created", tenant_id=tenant_id, org=DEMO_TENANT_NAME)
    return tenant_id, True


async def _seed_sales_and_transactions(session, tenant_id: str) -> None:
    """Insert the sample sales and acquirer transactions for the demo tenant."""
    sale_repo = PostgreSQLSaleRepository(session)
    transaction_repo = PostgreSQLTransactionRepository(session)

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

    logger.info("sales_transactions_seeded", sales=100, transactions=95, tenant_id=tenant_id)


async def _ensure_test_user(session, tenant_id: str) -> bool:
    """Create the ``test@example.com`` login if it does not already exist.

    Returns ``True`` when the user was created, ``False`` when it already
    existed (idempotent behaviour).
    """
    existing = await session.execute(
        select(UserModel).where(UserModel.email == TEST_USER_EMAIL)
    )
    if existing.scalar_one_or_none() is not None:
        logger.info("test_user_exists", email=TEST_USER_EMAIL)
        return False

    hasher = PasswordHasher()
    user = UserModel(
        id=str(uuid4()),
        tenant_id=tenant_id,
        email=TEST_USER_EMAIL,
        password_hash=hasher.hash_password(TEST_USER_PASSWORD),
        full_name="Test User MVP",
        is_active=True,
        roles=["user", "admin"],
    )
    session.add(user)
    await session.flush()
    logger.info("test_user_created", email=TEST_USER_EMAIL, tenant_id=tenant_id)
    return True


async def seed_data() -> None:
    """Insere dados de exemplo para ambiente de desenvolvimento (idempotente)."""
    database_url = DEFAULT_DB_URL
    database = Database(database_url)
    engine = database.engine

    from urllib.parse import urlparse, urlunparse

    _parsed = urlparse(database_url)
    _safe_url = urlunparse(
        _parsed._replace(netloc=f"{_parsed.username}:***@{_parsed.hostname}:{_parsed.port}")
    )
    logger.info("database_initialized", url=_safe_url)

    # Garante que as tabelas existem antes de popular dados
    await check_tables_exist(engine)

    async for session in database.get_session():
        tenant_id, tenant_created = await _get_or_create_tenant(session)

        if tenant_created:
            await _seed_sales_and_transactions(session, tenant_id)
        else:
            logger.info("sample_data_skipped", reason="tenant already seeded")

        user_created = await _ensure_test_user(session, tenant_id)

        logger.info(
            "seed_completed",
            tenant_id=tenant_id,
            tenant_created=tenant_created,
            user_created=user_created,
        )
        print(
            "✅ Seed idempotente concluído — tenant:",
            tenant_id,
            "| usuário de teste:",
            TEST_USER_EMAIL,
        )

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
