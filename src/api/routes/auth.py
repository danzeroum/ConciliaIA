"""Authentication routes with database-backed validation."""

from __future__ import annotations

from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
import structlog

from src.api import dependencies
from src.infrastructure.repositories.postgresql_user_repository import PostgreSQLUserRepository
from src.infrastructure.security import JWTHandler, PasswordHasher

logger = structlog.get_logger(__name__)

router = APIRouter(tags=["authentication"])


class LoginRequest(BaseModel):
    """Payload received when a user attempts to login."""

    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    """Response returned after a successful authentication."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class RefreshRequest(BaseModel):
    """Payload for requesting token refresh."""

    refresh_token: str


@router.post("/login", response_model=LoginResponse)
async def login(
    request: LoginRequest,
    jwt_handler: JWTHandler = Depends(dependencies.get_jwt_handler),
    password_hasher: PasswordHasher = Depends(dependencies.get_password_hasher),
    user_repository: PostgreSQLUserRepository = Depends(dependencies.get_user_repository),
) -> LoginResponse:
    """Authenticate a user using email and password."""

    user = await user_repository.find_by_email(request.email)
    if user is None:
        logger.warning("login_failed_user_not_found", email=request.email)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    if not user.is_active:
        logger.warning("login_failed_inactive_user", user_id=str(user.id))
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )

    password_valid = password_hasher.verify_password(request.password, user.password_hash)
    if not password_valid:
        logger.warning("login_failed_invalid_password", user_id=str(user.id), email=user.email)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    jti_access = str(uuid4())
    jti_refresh = str(uuid4())

    access_token = jwt_handler.create_access_token(
        user_id=str(user.id),
        tenant_id=str(user.tenant_id),
        email=user.email,
        roles=user.roles,
        jti=jti_access,
    )

    refresh_token = jwt_handler.create_refresh_token(
        user_id=str(user.id),
        tenant_id=str(user.tenant_id),
        jti=jti_refresh,
        email=user.email,
        roles=user.roles,
    )

    logger.info(
        "user_login_successful",
        user_id=str(user.id),
        tenant_id=str(user.tenant_id),
        email=user.email,
    )

    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=900,
    )


@router.post("/refresh", response_model=LoginResponse)
async def refresh_token(
    request: RefreshRequest,
    jwt_handler: JWTHandler = Depends(dependencies.get_jwt_handler),
) -> LoginResponse:
    """Refresh an access token using a valid refresh token."""

    token_data = jwt_handler.verify_token(request.refresh_token)
    if token_data is None or token_data.token_type != "refresh":
        logger.warning("token_refresh_failed", reason="invalid_token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    jti_access = str(uuid4())
    jti_refresh = str(uuid4())

    access_token = jwt_handler.create_access_token(
        user_id=token_data.sub,
        tenant_id=token_data.tenant_id,
        email=token_data.email or "",
        roles=token_data.roles,
        jti=jti_access,
    )

    new_refresh_token = jwt_handler.create_refresh_token(
        user_id=token_data.sub,
        tenant_id=token_data.tenant_id,
        jti=jti_refresh,
        email=token_data.email,
        roles=token_data.roles,
    )

    logger.info("token_refreshed", user_id=token_data.sub)

    return LoginResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
        expires_in=900,
    )


@router.post("/logout")
async def logout() -> dict[str, str]:
    """Logout endpoint placeholder (token invalidation is client-managed)."""

    logger.info("user_logout")
    return {"message": "Logged out successfully"}
