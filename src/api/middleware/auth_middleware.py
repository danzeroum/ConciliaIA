"""Authentication middleware for FastAPI."""

from __future__ import annotations

from fastapi import HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials
import structlog

from src.infrastructure.security import JWTHandler

logger = structlog.get_logger(__name__)


class AuthMiddleware:
    """Callable helper that verifies JWT tokens."""

    def __init__(self, jwt_handler: JWTHandler) -> None:
        self.jwt_handler = jwt_handler
        self.logger = logger.bind(middleware="AuthMiddleware")

    async def __call__(
        self, request: Request, credentials: HTTPAuthorizationCredentials
    ) -> dict:
        token = credentials.credentials
        token_data = self.jwt_handler.verify_token(token)
        if not token_data:
            self.logger.warning("authentication_failed", path=str(request.url.path))
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        request.state.user_id = token_data.sub
        request.state.tenant_id = token_data.tenant_id
        request.state.email = token_data.email
        request.state.roles = token_data.roles or []

        self.logger.debug(
            "authentication_successful",
            user_id=token_data.sub,
            tenant_id=token_data.tenant_id,
        )
        return {
            "user_id": token_data.sub,
            "tenant_id": token_data.tenant_id,
            "email": token_data.email,
            "roles": token_data.roles or [],
        }


__all__ = ["AuthMiddleware"]
