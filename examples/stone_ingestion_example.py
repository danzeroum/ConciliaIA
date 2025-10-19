"""Example: ingest Stone API transactions."""

from __future__ import annotations

import asyncio
from datetime import date

from src.infrastructure.acquirers import StoneAPIClient, StoneParser
from src.infrastructure.persistence.database import Database
from src.infrastructure.persistence.repositories.postgresql_transaction_repository import (
    PostgreSQLTransactionRepository,
)


async def main() -> None:
    database = Database(
        "postgresql+asyncpg://btv_user:btv_password@localhost:5432/conciliaai"
    )

    async for session in database.get_session():
        transaction_repo = PostgreSQLTransactionRepository(session)
        client = StoneAPIClient(
            client_id="your_client_id",
            client_secret="your_client_secret",
            stone_code="your_stone_code",
        )

        start_date = date(2023, 1, 1)
        end_date = date(2023, 1, 31)
        print(f"📥 Fetching Stone transactions from {start_date} to {end_date}...")
        raw_transactions = await client.fetch_transactions(start_date, end_date)
        print(f"✅ Fetched {len(raw_transactions)} transactions")

        parser = StoneParser()
        print("🔍 Parsing transactions...")
        transactions = parser.parse(raw_transactions, tenant_id="tenant-123")
        print(f"✅ Parsed {len(transactions)} transactions")

        print("💾 Saving to database...")
        for transaction in transactions:
            await transaction_repo.save(transaction)
        await session.commit()
        print(f"✅ Ingestion completed: {len(transactions)} transactions saved")

    await database.close()


if __name__ == "__main__":
    asyncio.run(main())
