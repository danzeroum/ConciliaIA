"""Authentication routes."""

from __future__ import annotations

from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
import structlog

from src.api import dependencies
from src.infrastructure.security import JWTHandler, PasswordHasher

logger = structlog.get_logger(__name__)

router = APIRouter(tags=["authentication"])


# Temporary test user for MVP
TEST_USER = {
    "user_id": "test-user-001",
    "tenant_id": "test-tenant-001",
    "email": "test@example.com",
    "password_hash": (
        "$argon2id$v=19$m=65536,t=3,p=4$VOVrn54a+GS8dOngLF0QQg$VksnxcG5q2UuH1n3TFAnCcDF18CFRhJUMHWQ8ETHW9Y"
    ),  # Hash gerado pelo script de senha de teste
    "roles": ["user", "admin"],
    "name": "Test User",
}


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class RefreshRequest(BaseModel):
    refresh_token: str


@router.post("/login", response_model=LoginResponse)
async def login(
    request: LoginRequest,
    jwt_handler: JWTHandler = Depends(dependencies.get_jwt_handler),
    password_hasher: PasswordHasher = Depends(dependencies.get_password_hasher),
) -> LoginResponse:
    """
    Temporary login endpoint with hardcoded test user.
    TODO: Replace with real database lookup and password verification.
    """

    # Validate email
    if request.email != TEST_USER["email"]:
        logger.warning(
            "login_failed_invalid_email",
            email=request.email,
            reason="user_not_found",
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    # Validate password
    try:
        password_valid = password_hasher.verify_password(
            request.password,
            TEST_USER["password_hash"],
        )
    except Exception as e:  # pragma: no cover - defensive
        logger.warning(
            "login_failed_invalid_password",
            email=request.email,
            reason="password_mismatch",
            error=str(e),
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    if not password_valid:
        logger.warning(
            "login_failed_invalid_password",
            email=request.email,
            reason="password_mismatch",
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    # Generate tokens
    jti_access = str(uuid4())
    jti_refresh = str(uuid4())

    access_token = jwt_handler.create_access_token(
        user_id=TEST_USER["user_id"],
        tenant_id=TEST_USER["tenant_id"],
        email=TEST_USER["email"],
        roles=TEST_USER["roles"],
        jti=jti_access,
    )

    refresh_token = jwt_handler.create_refresh_token(
        user_id=TEST_USER["user_id"],
        tenant_id=TEST_USER["tenant_id"],
        jti=jti_refresh,
        email=TEST_USER["email"],
        roles=TEST_USER["roles"],
    )

    logger.info(
        "user_login_successful",
        user_id=TEST_USER["user_id"],
        tenant_id=TEST_USER["tenant_id"],
        email=TEST_USER["email"],
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
    token_data = jwt_handler.verify_token(request.refresh_token)
    if not token_data or token_data.token_type != "refresh":
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
    refresh_token = jwt_handler.create_refresh_token(
        user_id=token_data.sub,
        tenant_id=token_data.tenant_id,
        jti=jti_refresh,
        email=token_data.email,
        roles=token_data.roles,
    )

    logger.info("token_refreshed", user_id=token_data.sub)

    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=900,
    )


@router.post("/logout")
async def logout() -> dict:
    logger.info("user_logout")
    return {"message": "Logged out successfully"}
