"""Seed database with sample data for development."""

from __future__ import annotations

import asyncio
import os
import sys
from datetime import date, timedelta
from decimal import Decimal
from uuid import uuid4

# Adiciona o diretório raiz do projeto (que é o pai de 'scripts') ao sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# FIM DO CÓDIGO DE AJUSTE DE PATH

from src.domain.entities import AcquirerTransaction, Sale
from src.domain.entities.tenant import TenantTier
from src.infrastructure.persistence.models import TenantModel # <--- IMPORTAÇÃO CRUCIAL (ASSUME que você a definiu em models.py)
from src.domain.value_objects import Acquirer, Money
from src.infrastructure.persistence.database import Database
from src.infrastructure.persistence.repositories.postgresql_sale_repository import PostgreSQLSaleRepository
from src.infrastructure.persistence.repositories.postgresql_transaction_repository import (
    PostgreSQLTransactionRepository,
)


async def seed_data() -> None:
    """Seed database with sample data."""
    database_url = "postgresql+asyncpg://btv_user:btv_password@postgres:5432/conciliaai"
    database = Database(database_url)

    async for session in database.get_session():
        sale_repo = PostgreSQLSaleRepository(session)
        transaction_repo = PostgreSQLTransactionRepository(session)

        tenant_id = str(uuid4())
        
        # --- LÓGICA CORRIGIDA: INSERIR TenantModel (Modelo ORM) ---
        tenant_model = TenantModel(
            id=tenant_id,
            org_name="Mariana - E-commerce Owner", # Usa campo correto
            cnpj="99999999000100",                 # CNPJ de placeholder
            tier=TenantTier.ALPHA.value,           # Tier de placeholder (passa o valor da Enum)
            active=True,
        )
        session.add(tenant_model)
        await session.flush() # Persiste o tenant_id antes de usá-lo
        # --- FIM DA LÓGICA CORRIGIDA ---

        print(f"🌱 Seeding data for tenant: {tenant_id}")

        for i in range(100):
            amount = Decimal(100 + i * 10)
            sale = Sale(
                id=str(uuid4()),
                tenant_id=tenant_id, # ID do tenant recém-criado
                nsu=f"NSU{i:09d}",
                amount=Money(amount),
                date=date.today() - timedelta(days=i % 30),
                payment_method="credit_card" if i % 2 == 0 else "debit_card",
            )
            await sale_repo.save(sale)

            if i < 95:
                transaction = AcquirerTransaction(
                    id=str(uuid4()),
                    tenant_id=tenant_id, # ID do tenant recém-criado
                    acquirer=Acquirer.CIELO if i % 3 == 0 else Acquirer.REDE,
                    nsu=f"NSU{i:09d}",
                    amount=Money(amount),
                    transaction_date=date.today() - timedelta(days=i % 30),
                    mdr_amount=Money(amount * Decimal("0.025")),
                    net_amount=Money(amount * Decimal("0.975")),
                )
                await transaction_repo.save(transaction)

        print("✅ Seeded 100 sales and 95 transactions")
        # O commit é tratado pelo get_session()

    await database.close()


if __name__ == "__main__":
    asyncio.run(seed_data())