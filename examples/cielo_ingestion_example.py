"""Example: ingest Cielo EDI files.

Before running, set the required environment variables:
  DATABASE_URL=postgresql+asyncpg://user:password@host:5432/dbname
  CIELO_SFTP_HOST=sftp.cielo.com.br
  CIELO_SFTP_USERNAME=your_username
  CIELO_SFTP_PASSWORD=your_password
  CIELO_EC_NUMBER=your_ec_number
"""

from __future__ import annotations

import asyncio
import os
from datetime import date
from pathlib import Path

from src.infrastructure.acquirers import CieloEDIClient, CieloEDIParser
from src.infrastructure.persistence.database import Database
from src.infrastructure.persistence.repositories.postgresql_transaction_repository import (
    PostgreSQLTransactionRepository,
)


async def main() -> None:
    database_url = os.environ["DATABASE_URL"]
    database = Database(database_url)

    async for session in database.get_session():
        transaction_repo = PostgreSQLTransactionRepository(session)
        client = CieloEDIClient(
            host=os.getenv("CIELO_SFTP_HOST", "sftp.cielo.com.br"),
            port=22,
            username=os.environ["CIELO_SFTP_USERNAME"],
            password=os.environ["CIELO_SFTP_PASSWORD"],
            ec_number=os.environ["CIELO_EC_NUMBER"],
        )

        target_date = date.today()
        local_path = Path("/tmp/cielo")
        print(f"📥 Downloading Cielo EDI for {target_date}...")
        file_path = await client.download_file(target_date, local_path)
        if not file_path:
            print("❌ File not found")
            return

        print(f"✅ Downloaded: {file_path}")
        parser = CieloEDIParser()
        with file_path.open("r", encoding="latin-1") as fh:
            edi_content = fh.read()
        print("🔍 Parsing EDI file...")
        transactions = parser.parse(edi_content, tenant_id="tenant-123")
        print(f"✅ Parsed {len(transactions)} transactions")

        print("💾 Saving to database...")
        for transaction in transactions:
            await transaction_repo.save(transaction)
        await session.commit()
        print(f"✅ Ingestion completed: {len(transactions)} transactions saved")

    await database.close()


if __name__ == "__main__":
    asyncio.run(main())
