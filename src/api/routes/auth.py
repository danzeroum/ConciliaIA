"""Authentication routes with database-backed validation."""

from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from fastapi import APIRouter, Body, Depends, HTTPException, Request, status
from pydantic import BaseModel, EmailStr
import structlog

from src.api import dependencies
from src.api.dependencies import get_current_user
from src.infrastructure.repositories.postgresql_user_repository import PostgreSQLUserRepository
from src.infrastructure.security import (
    JWTHandler,
    LoginAttemptTracker,
    PasswordHasher,
    TokenBlocklist,
)

logger = structlog.get_logger(__name__)

router = APIRouter(tags=["authentication"])


def _revoke_jti(blocklist: TokenBlocklist, jti: str | None, exp: datetime | None) -> None:
    """Revoke ``jti`` until its underlying token would have expired."""
    if not jti or exp is None:
        return
    blocklist.revoke(jti, (exp - datetime.utcnow()).total_seconds())


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
    attempts: LoginAttemptTracker = Depends(dependencies.get_login_attempt_tracker),
) -> LoginResponse:
    """Authenticate a user using email and password."""

    attempt_key = request.email.lower()
    locked_for = attempts.seconds_until_unlock(attempt_key)
    if locked_for:
        logger.warning("login_blocked_locked_out", email=request.email, retry_after=locked_for)
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many failed attempts. Please try again later.",
            headers={"Retry-After": str(locked_for)},
        )

    user = await user_repository.find_by_email(request.email)
    if user is None:
        attempts.register_failure(attempt_key)
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
        attempts.register_failure(attempt_key)
        logger.warning("login_failed_invalid_password", user_id=str(user.id), email=user.email)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    attempts.reset(attempt_key)

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
    blocklist: TokenBlocklist = Depends(dependencies.get_token_blocklist),
) -> LoginResponse:
    """Refresh an access token using a valid refresh token (rotates it)."""

    token_data = jwt_handler.verify_token(request.refresh_token)
    if token_data is None or token_data.token_type != "refresh":
        logger.warning("token_refresh_failed", reason="invalid_token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    if blocklist.is_revoked(token_data.jti):
        logger.warning("token_refresh_reuse_detected", user_id=token_data.sub)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token has been revoked",
        )

    # Rotation: the presented refresh token cannot be reused after this call.
    _revoke_jti(blocklist, token_data.jti, token_data.exp)

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


class UserMeResponse(BaseModel):
    """Authenticated user profile extracted from the JWT."""

    id: str
    email: str
    name: str
    roles: list[str]
    tenant_id: str


@router.get("/me", response_model=UserMeResponse)
async def get_me(user: dict = Depends(get_current_user)) -> UserMeResponse:
    """Return the profile of the currently authenticated user."""

    return UserMeResponse(
        id=user.get("sub", ""),
        email=user.get("email", ""),
        name=user.get("name", user.get("email", "")),
        roles=user.get("roles", []),
        tenant_id=user.get("tenant_id", ""),
    )


class LogoutRequest(BaseModel):
    """Optional payload allowing the refresh token to be revoked on logout."""

    refresh_token: str | None = None


@router.post("/logout")
async def logout(
    request: Request,
    body: LogoutRequest = Body(default=LogoutRequest()),
    jwt_handler: JWTHandler = Depends(dependencies.get_jwt_handler),
    blocklist: TokenBlocklist = Depends(dependencies.get_token_blocklist),
) -> dict[str, str]:
    """Revoke the current access token (and refresh token, when provided)."""

    auth_header = request.headers.get("Authorization", "")
    if auth_header.lower().startswith("bearer "):
        access_data = jwt_handler.verify_token(auth_header[7:].strip())
        if access_data is not None:
            _revoke_jti(blocklist, access_data.jti, access_data.exp)

    if body and body.refresh_token:
        refresh_data = jwt_handler.verify_token(body.refresh_token)
        if refresh_data is not None and refresh_data.token_type == "refresh":
            _revoke_jti(blocklist, refresh_data.jti, refresh_data.exp)

    logger.info("user_logout")
    return {"message": "Logged out successfully"}
