#!/usr/bin/env python3
"""Seed test user for MVP authentication."""

import asyncio
import json
import os
import sys
from pathlib import Path

# Add project root to path BEFORE imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# NOW import project modules
from src.infrastructure.database import Database
from src.infrastructure.security import PasswordHasher


async def seed_test_user():
    """Create test user in database."""

    database = Database(
        host=os.getenv("POSTGRES_HOST", "postgres"),
        port=int(os.getenv("POSTGRES_PORT", "5432")),
        user=os.getenv("POSTGRES_USER", "conciliaai"),
        password=os.getenv("POSTGRES_PASSWORD", "dev_password_2025"),
        database=os.getenv("POSTGRES_DB", "conciliaai"),
    )

    await database.connect()
    print("✅ Connected to database")

    try:
        existing = await database.fetch_one(
            "SELECT id FROM users WHERE email = $1",
            "test@example.com",
        )
        if existing:
            print("⚠️  Test user already exists, skipping creation.")
            return

        tenant = await database.fetch_one("SELECT id FROM tenants ORDER BY created_at LIMIT 1")
        if tenant is None:
            raise RuntimeError("No tenant found. Run the main seed script before creating the test user.")

        tenant_id = tenant["id"]
        print(f"📦 Using tenant: {tenant_id}")

        password_hasher = PasswordHasher()
        password_hash = password_hasher.hash_password("SecurePassword123!")

        insert_query = """
            INSERT INTO users (
                tenant_id,
                email,
                password_hash,
                full_name,
                is_active,
                roles
            )
            VALUES ($1, $2, $3, $4, $5, $6::jsonb)
            RETURNING id, email, full_name
        """

        user = await database.fetch_one(
            insert_query,
            tenant_id,
            "test@example.com",
            password_hash,
            "Test User MVP",
            True,
            json.dumps(["user", "admin"]),
        )

        if user is None:
            raise RuntimeError("Failed to insert test user")

        print("✅ Test user created successfully")
        print(f"   ID: {user['id']}")
        print(f"   Email: {user['email']}")
        print(f"   Name: {user['full_name']}")
        print("\n🔐 Credentials:")
        print("   Email: test@example.com")
        print("   Password: SecurePassword123!")
    finally:
        await database.close()
        print("🔚 Database connection closed")


if __name__ == "__main__":
    asyncio.run(seed_test_user())
