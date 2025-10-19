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
    # Placeholder user lookup logic
    user_id = "user-123"
    tenant_id = "tenant-123"
    email = request.email
    roles = ["user"]

    # TODO: Replace with real password verification
    # password_valid = password_hasher.verify_password(request.password, stored_hash)
    # if not password_valid:
    #     raise HTTPException(status_code=401, detail="Invalid credentials")
    _ = password_hasher

    jti_access = str(uuid4())
    jti_refresh = str(uuid4())

    access_token = jwt_handler.create_access_token(
        user_id=user_id,
        tenant_id=tenant_id,
        email=email,
        roles=roles,
        jti=jti_access,
    )

    refresh_token = jwt_handler.create_refresh_token(
        user_id=user_id,
        tenant_id=tenant_id,
        jti=jti_refresh,
        email=email,
        roles=roles,
    )

    logger.info("user_login_successful", user_id=user_id, tenant_id=tenant_id)

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
