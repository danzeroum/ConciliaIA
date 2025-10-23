"""PostgreSQL-backed implementation of the user repository."""

from __future__ import annotations

from uuid import UUID

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.user import User
from src.domain.repositories.user_repository import UserRepository
from src.infrastructure.persistence.models import UserModel

logger = structlog.get_logger(__name__)


class PostgreSQLUserRepository(UserRepository):
    """User repository using SQLAlchemy and PostgreSQL."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._logger = logger.bind(repository="PostgreSQLUserRepository")

    async def find_by_email(self, email: str) -> User | None:
        """Return an active user identified by e-mail."""

        stmt = select(UserModel).where(
            UserModel.email == email,
            UserModel.is_active.is_(True),
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if model is None:
            self._logger.debug("user_not_found", email=email)
            return None

        self._logger.debug("user_found", user_id=str(model.id), email=email)
        return self._to_entity(model)

    async def find_by_id(self, user_id: UUID) -> User | None:
        """Return an active user by identifier."""

        stmt = select(UserModel).where(
            UserModel.id == user_id,
            UserModel.is_active.is_(True),
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()

        if model is None:
            self._logger.debug("user_not_found", user_id=str(user_id))
            return None

        self._logger.debug("user_found", user_id=str(user_id))
        return self._to_entity(model)

    def _to_entity(self, model: UserModel) -> User:
        roles_value = model.roles or []
        if isinstance(roles_value, tuple):
            roles_list = list(roles_value)
        elif isinstance(roles_value, list):
            roles_list = roles_value
        else:
            roles_list = [str(roles_value)] if roles_value else []
        return User(
            id=model.id,
            tenant_id=model.tenant_id,
            email=model.email,
            password_hash=model.password_hash,
            full_name=model.full_name,
            is_active=model.is_active,
            roles=roles_list,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )


__all__ = ["PostgreSQLUserRepository"]
