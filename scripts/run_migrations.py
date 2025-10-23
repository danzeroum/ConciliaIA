#!/usr/bin/env python3
"""Run database migrations sequentially."""

from __future__ import annotations

import asyncio
import os
from pathlib import Path

from src.infrastructure.database import Database


async def run_migrations() -> None:
    """Execute all SQL migration files in order."""

    database = Database(
        host=os.getenv("POSTGRES_HOST", "postgres"),
        port=int(os.getenv("POSTGRES_PORT", "5432")),
        user=os.getenv("POSTGRES_USER", "btv_user"),
        password=os.getenv("POSTGRES_PASSWORD", "btv_password"),
        database=os.getenv("POSTGRES_DB", "conciliaai"),
    )

    migrations_dir = Path(__file__).resolve().parent.parent / "migrations"
    migration_files = sorted(migrations_dir.glob("*.sql"))

    if not migration_files:
        print("⚠️  No migration files found, skipping execution.")
        return

    try:
        await database.connect()
        print("✅ Connected to database")

        for path in migration_files:
            print(f"🔄 Running migration: {path.name}")
            sql = path.read_text(encoding="utf-8")
            if sql.strip():
                await database.execute(sql)
            print(f"✅ Completed migration: {path.name}")

        print(f"\n✅ All {len(migration_files)} migrations executed successfully")
    finally:
        await database.close()
        print("🔚 Database connection closed")


if __name__ == "__main__":
    asyncio.run(run_migrations())
