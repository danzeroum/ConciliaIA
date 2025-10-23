#!/usr/bin/env python3
"""Run database migrations."""

import asyncio
import os
import sys
from pathlib import Path

# Add project root to path BEFORE imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# NOW import project modules
from src.infrastructure.database import Database


async def run_migrations():
    """Execute all SQL migration files."""

    database = Database(
        host=os.getenv("POSTGRES_HOST", "postgres"),
        port=int(os.getenv("POSTGRES_PORT", "5432")),
        user=os.getenv("POSTGRES_USER", "conciliaai"),
        password=os.getenv("POSTGRES_PASSWORD", "dev_password_2025"),
        database=os.getenv("POSTGRES_DB", "conciliaai"),
    )

    try:
        await database.connect()
        print("✅ Connected to database")

        migrations_dir = project_root / "migrations"
        migration_files = sorted(migrations_dir.glob("*.sql"))

        if not migration_files:
            print("⚠️  No migration files found")
            return

        for migration_file in migration_files:
            print(f"🔄 Running: {migration_file.name}")

            with open(migration_file, "r", encoding="utf-8") as f:
                sql = f.read()

            # Execute migration
            try:
                await database.execute(sql)
                print(f"✅ Completed: {migration_file.name}")
            except Exception as e:
                print(f"❌ Failed: {migration_file.name}")
                print(f"   Error: {e}")
                raise

        print(f"\n✅ All {len(migration_files)} migrations completed successfully")

    except Exception as e:
        print(f"❌ Migration error: {e}")
        raise
    finally:
        await database.close()
        print("🔚 Database connection closed")


if __name__ == "__main__":
    asyncio.run(run_migrations())
