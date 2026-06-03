"""Example: ingest Stone API transactions.

Before running, set the required environment variables:
  DATABASE_URL=postgresql+asyncpg://user:password@host:5432/dbname
  STONE_CLIENT_ID=your_client_id
  STONE_CLIENT_SECRET=your_client_secret
  STONE_CODE=your_stone_code
"""

from __future__ import annotations

import asyncio
import os
from datetime import date

from src.infrastructure.acquirers import StoneAPIClient, StoneParser
from src.infrastructure.persistence.database import Database
from src.infrastructure.persistence.repositories.postgresql_transaction_repository import (
    PostgreSQLTransactionRepository,
)


async def main() -> None:
    database_url = os.environ["DATABASE_URL"]
    database = Database(database_url)

    async for session in database.get_session():
        transaction_repo = PostgreSQLTransactionRepository(session)
        client = StoneAPIClient(
            client_id=os.environ["STONE_CLIENT_ID"],
            client_secret=os.environ["STONE_CLIENT_SECRET"],
            stone_code=os.environ["STONE_CODE"],
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
