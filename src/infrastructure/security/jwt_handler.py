"""JWT token generation and validation utilities."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import List

from jose import JWTError, jwt
from pydantic import BaseModel, ConfigDict, Field
import structlog

logger = structlog.get_logger(__name__)


class TokenData(BaseModel):
    """JWT token payload data."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    sub: str
    tenant_id: str
    email: str | None = None
    roles: List[str] = Field(default_factory=list)
    exp: datetime
    iat: datetime
    jti: str | None = None
    token_type: str | None = None


class JWTHandler:
    """Handle JWT token generation and validation."""

    def __init__(
        self,
        secret_key: str,
        algorithm: str = "HS256",
        access_token_expire_minutes: int = 15,
        refresh_token_expire_days: int = 7,
    ) -> None:
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.access_token_expire = timedelta(minutes=access_token_expire_minutes)
        self.refresh_token_expire = timedelta(days=refresh_token_expire_days)
        self.logger = logger.bind(component="JWTHandler")

    def create_access_token(
        self,
        user_id: str,
        tenant_id: str,
        email: str,
        roles: List[str],
        jti: str,
    ) -> str:
        now = datetime.utcnow()
        expire = now + self.access_token_expire
        payload = {
            "sub": user_id,
            "tenant_id": tenant_id,
            "email": email,
            "roles": roles,
            "type": "access",
            "exp": expire,
            "iat": now,
            "jti": jti,
        }
        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        self.logger.debug(
            "access_token_created", user_id=user_id, tenant_id=tenant_id, expires_at=expire.isoformat()
        )
        return token

    def create_refresh_token(
        self,
        user_id: str,
        tenant_id: str,
        jti: str,
        email: str | None = None,
        roles: List[str] | None = None,
    ) -> str:
        now = datetime.utcnow()
        expire = now + self.refresh_token_expire
        payload = {
            "sub": user_id,
            "tenant_id": tenant_id,
            "type": "refresh",
            "exp": expire,
            "iat": now,
            "jti": jti,
        }
        if email:
            payload["email"] = email
        if roles:
            payload["roles"] = roles
        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        self.logger.debug(
            "refresh_token_created", user_id=user_id, tenant_id=tenant_id, expires_at=expire.isoformat()
        )
        return token

    def verify_token(self, token: str) -> TokenData | None:
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
        except JWTError as exc:
            self.logger.warning("token_verification_failed", error=str(exc))
            return None

        if "sub" not in payload or "tenant_id" not in payload:
            self.logger.warning("token_validation_failed", reason="missing_fields")
            return None

        try:
            exp = datetime.utcfromtimestamp(payload["exp"])
        except (TypeError, ValueError, KeyError):
            exp = datetime.utcnow()
        try:
            iat = datetime.utcfromtimestamp(payload["iat"])
        except (TypeError, ValueError, KeyError):
            iat = datetime.utcnow()

        token_data = TokenData(
            sub=payload["sub"],
            tenant_id=payload["tenant_id"],
            email=payload.get("email"),
            roles=payload.get("roles", []),
            exp=exp,
            iat=iat,
            jti=payload.get("jti"),
            token_type=payload.get("type"),
        )
        self.logger.debug("token_verified", user_id=token_data.sub)
        return token_data

    def decode_token_unsafe(self, token: str) -> dict | None:
        try:
            return jwt.decode(token, options={"verify_signature": False})
        except JWTError:
            return None


__all__ = ["JWTHandler", "TokenData"]
