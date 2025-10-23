#!/usr/bin/env python3
"""Complete MVP seed: tenant + test user."""

import asyncio
import json
import os
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.infrastructure.database import Database
from src.infrastructure.security import PasswordHasher


async def seed_mvp() -> None:
    """Seed tenant and test user for MVP."""

    database = Database(
        host=os.getenv("POSTGRES_HOST", "postgres"),
        port=int(os.getenv("POSTGRES_PORT", "5432")),
        user=os.getenv("POSTGRES_USER", "btv_user"),
        password=os.getenv("POSTGRES_PASSWORD", "btv_password"),
        database=os.getenv("POSTGRES_DB", "conciliaai"),
    )

    try:
        await database.connect()
        print("✅ Connected to database")

        # ========== STEP 1: Create tenant ==========
        print("\n📦 Step 1: Creating tenant...")

        tenant = await database.fetch_one(
            "SELECT id, org_name FROM tenants LIMIT 1"
        )

        if tenant:
            print(f"   ✅ Tenant exists: {tenant['org_name']} ({tenant['id']})")
            tenant_id = tenant["id"]
        else:
            tenant = await database.fetch_one(
                """
                INSERT INTO tenants (org_name, cnpj, tier, active)
                VALUES ($1, $2, $3, $4)
                RETURNING id, org_name
                """,
                "ConciliaAI MVP",
                "00000000000001",
                "alpha",
                True,
            )
            tenant_id = tenant["id"]
            print(f"   ✅ Tenant created: {tenant['org_name']} ({tenant_id})")

        # ========== STEP 2: Create test user ==========
        print("\n👤 Step 2: Creating test user...")

        user = await database.fetch_one(
            "SELECT id, email FROM users WHERE email = $1",
            "test@example.com",
        )

        if user:
            print(f"   ⚠️  User exists: {user['email']} ({user['id']})")
            return

        hasher = PasswordHasher()
        password_hash = hasher.hash_password("SecurePassword123!")

        user = await database.fetch_one(
            """
            INSERT INTO users (
                tenant_id, email, password_hash,
                full_name, is_active, roles
            )
            VALUES ($1, $2, $3, $4, $5, $6::jsonb)
            RETURNING id, email, full_name
            """,
            tenant_id,
            "test@example.com",
            password_hash,
            "Test User MVP",
            True,
            json.dumps(["user", "admin"]),
        )

        print(f"   ✅ User created: {user['email']} ({user['id']})")

        # ========== SUMMARY ==========
        print("\n" + "=" * 60)
        print("🎉 MVP SEED COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print("\n🔐 Login Credentials:")
        print("   Email:    test@example.com")
        print("   Password: SecurePassword123!")
        print(f"\n🏢 Tenant:   {tenant['org_name']}")
        print(f"   ID:       {tenant_id}")
        print(f"\n👤 User:     {user['full_name']}")
        print(f"   ID:       {user['id']}")
        print("\n🚀 Next Steps:")
        print("   1. Test login: curl -X POST http://localhost:8000/auth/login \\")
        print('        -H "Content-Type: application/json" \\')
        print('        -d \'{"email":"test@example.com","password":"SecurePassword123!"}\'')
        print("   2. Open frontend: http://localhost:3000")
        print("   3. Login and start using ConciliaAI MVP!")
        print()

    except Exception as e:  # pragma: no cover - script feedback
        print(f"\n❌ Seed failed: {e}")
        raise
    finally:
        await database.close()
        print("🔚 Database connection closed\n")


if __name__ == "__main__":
    asyncio.run(seed_mvp())
