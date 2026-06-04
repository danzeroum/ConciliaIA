"""Pytest configuration and fixtures."""

from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path
from typing import AsyncGenerator, Iterator
from uuid import UUID

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

DEFAULT_TEST_DATABASE_URL = "postgresql+asyncpg://test_user:test_password@postgres:5432/conciliaai_test"

TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", DEFAULT_TEST_DATABASE_URL)

os.environ["SECRET_KEY"] = os.getenv("SECRET_KEY", "test-only-secret-key-not-for-production")
os.environ["DATABASE_URL"] = TEST_DATABASE_URL
os.environ["REDIS_HOST"] = "redis"

from src.api import dependencies
from src.api.main import app
from src.api.middleware import AuthMiddleware, RateLimitMiddleware
from src.infrastructure.persistence.models import Base, TenantModel, UserModel
from src.infrastructure.security import JWTHandler, RateLimiter
from src.infrastructure.security.password_hasher import PasswordHasher

TENANT_TEST_ID = "00000000-0000-0000-0000-000000000001"
USER_TEST_ID = "00000000-0000-0000-0000-000000000002"
TEST_PASSWORD = "SecurePassword123!"


@pytest.fixture(scope="session", autouse=True)
def configure_api_dependencies() -> Iterator[None]:
    """Ensure API dependencies are initialised for integration tests."""

    secret_key = os.environ.get("SECRET_KEY", "test-secret")

    dependencies.jwt_handler = JWTHandler(secret_key=secret_key)
    dependencies.password_hasher = PasswordHasher()
    dependencies.rate_limiter = RateLimiter(
        requests_per_minute=int(
            os.getenv(
                "RATE_LIMIT_REQUESTS_PER_MINUTE",
                os.getenv("RATE_LIMIT_PER_MINUTE", "100"),
            )
        )
    )
    dependencies.auth_middleware = AuthMiddleware(dependencies.jwt_handler)

    # Provide a fallback database so ``get_db_session`` never errors for requests
    # that do not go through the per-test ``db_session`` override (e.g. a request
    # that fails body validation before touching the DB).
    from src.infrastructure.persistence.database import Database

    dependencies.database = Database(TEST_DATABASE_URL)

    if not getattr(app.state, "rate_limit_middleware_installed", False):
        app.add_middleware(
            RateLimitMiddleware, rate_limiter=dependencies.rate_limiter
        )
        app.state.rate_limit_middleware_installed = True

    try:
        yield
    finally:
        dependencies.jwt_handler = None
        dependencies.password_hasher = None
        dependencies.rate_limiter = None
        dependencies.auth_middleware = None
        dependencies.database = None


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def db_engine() -> AsyncGenerator[AsyncEngine, None]:
    """Create test database engine."""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(db_engine: AsyncEngine) -> AsyncGenerator[AsyncSession, None]:
    """Provide an active async database session for each test."""

    async with db_engine.connect() as connection:
        await connection.begin()

        async with AsyncSession(connection, expire_on_commit=False) as session:
            # Route the application's ``get_db_session`` dependency to this same
            # transactional session so requests made over HTTP (e.g. the auth
            # endpoints) see the data created by the test fixtures.
            from src.api.dependencies import get_db_session

            app.dependency_overrides[get_db_session] = lambda: session
            try:
                yield session
            finally:
                app.dependency_overrides.pop(get_db_session, None)

        await connection.rollback()


@pytest_asyncio.fixture
async def test_tenant(db_session: AsyncSession) -> AsyncGenerator[TenantModel, None]:
    """Ensure a deterministic tenant exists for tests requiring foreign keys."""

    tenant = await db_session.get(TenantModel, UUID(TENANT_TEST_ID))

    if tenant is None:
        tenant = TenantModel(
            id=UUID(TENANT_TEST_ID),
            org_name="Test Tenant Org",
            cnpj="00000000000100",
            tier="alpha",
            active=True,
        )
        db_session.add(tenant)
    else:
        tenant.org_name = "Test Tenant Org"
        tenant.cnpj = "00000000000100"
        tenant.tier = "alpha"
        tenant.active = True

    await db_session.flush()
    await db_session.refresh(tenant)

    yield tenant


@pytest_asyncio.fixture
async def test_user(
    db_session: AsyncSession, test_tenant: TenantModel
) -> AsyncGenerator[UserModel, None]:
    """Ensure a deterministic user exists for authentication-related tests."""

    hasher = PasswordHasher()
    hashed_password = hasher.hash_password(TEST_PASSWORD)

    user = await db_session.get(UserModel, UUID(USER_TEST_ID))

    if user is None:
        user = UserModel(
            id=UUID(USER_TEST_ID),
            tenant_id=test_tenant.id,
            email="test@example.com",
            password_hash=hashed_password,
            full_name="Test User",
            roles=["user"],
            is_active=True,
        )
        db_session.add(user)
    else:
        user.tenant_id = test_tenant.id
        user.email = "test@example.com"
        user.password_hash = hashed_password
        user.role = "user"
        user.is_active = True

    await db_session.flush()
    await db_session.refresh(user)

    yield user
