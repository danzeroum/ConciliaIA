"""Async PostgreSQL repository implementations."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import List

import asyncpg

from src.domain.entities import AcquirerTransaction, Sale
from src.domain.value_objects import Money
from src.domain.repositories import SaleRepository, TransactionRepository


class PostgresSaleRepository(SaleRepository):
    """Async PostgreSQL repository for sales."""

    def __init__(self, pool: asyncpg.Pool) -> None:
        self.pool = pool

    async def find_by_date_range(
        self, tenant_id: str, start_date: date, end_date: date
    ) -> List[Sale]:
        query = """
            SELECT id, tenant_id, nsu, amount, date, payment_method, installments, created_at
            FROM sales
            WHERE tenant_id = $1
              AND date BETWEEN $2 AND $3
            ORDER BY date, nsu
        """

        async with self.pool.acquire() as connection:
            rows = await connection.fetch(query, tenant_id, start_date, end_date)

        return [
            Sale(
                id=str(row["id"]),
                tenant_id=str(row["tenant_id"]),
                nsu=row["nsu"],
                amount=Money(Decimal(str(row["amount"]))),
                date=row["date"],
                payment_method=row["payment_method"],
                installments=row["installments"],
                created_at=row["created_at"],
            )
            for row in rows
        ]

    async def save(self, sale: Sale) -> None:
        query = """
            INSERT INTO sales (id, tenant_id, nsu, amount, date, payment_method, installments)
            VALUES ($1, $2, $3, $4, $5, $6, $7)
        """

        async with self.pool.acquire() as connection:
            await connection.execute(
                query,
                sale.id,
                sale.tenant_id,
                str(sale.nsu),
                sale.amount.amount,
                sale.date,
                sale.payment_method,
                sale.installments,
            )


class PostgresTransactionRepository(TransactionRepository):
    """Async PostgreSQL repository for acquirer transactions."""

    def __init__(self, pool: asyncpg.Pool) -> None:
        self.pool = pool

    async def find_by_date_range(
        self, tenant_id: str, start_date: date, end_date: date
    ) -> List[AcquirerTransaction]:
        query = """
            SELECT id, tenant_id, acquirer, nsu, transaction_date, amount, mdr_amount, net_amount
            FROM acquirer_transactions
            WHERE tenant_id = $1
              AND transaction_date BETWEEN $2 AND $3
            ORDER BY transaction_date, nsu
        """

        async with self.pool.acquire() as connection:
            rows = await connection.fetch(query, tenant_id, start_date, end_date)

        transactions: List[AcquirerTransaction] = []
        for row in rows:
            transactions.append(
                AcquirerTransaction(
                    id=str(row["id"]),
                    tenant_id=str(row["tenant_id"]),
                    acquirer=row["acquirer"],
                    nsu=row["nsu"],
                    amount=Money(Decimal(str(row["amount"]))),
                    transaction_date=row["transaction_date"],
                    mdr_amount=Money(Decimal(str(row["mdr_amount"]))),
                    net_amount=Money(Decimal(str(row["net_amount"]))),
                )
            )

        return transactions


__all__ = ["PostgresSaleRepository", "PostgresTransactionRepository"]
