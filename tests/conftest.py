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

DEFAULT_TEST_DATABASE_URL = "postgresql+asyncpg://btv_user:btv_password@postgres:5432/conciliaai"

TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", DEFAULT_TEST_DATABASE_URL)

# Ensure critical security variables are available for the test environment
os.environ["SECRET_KEY"] = "sua_chave_secreta_deve_ser_longa_e_unica_para_o_teste_dev"
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
            yield session

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
            password=hashed_password,
            role="user",
            is_active=True,
        )
        db_session.add(user)
    else:
        user.tenant_id = test_tenant.id
        user.email = "test@example.com"
        user.password = hashed_password
        user.role = "user"
        user.is_active = True

    await db_session.flush()
    await db_session.refresh(user)

    yield user
