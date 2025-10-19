"""Secrets manager abstraction built on top of AWS Secrets Manager."""

from __future__ import annotations

import json
from typing import Dict, Optional

import boto3
import structlog
from botocore.exceptions import ClientError

logger = structlog.get_logger(__name__)


class SecretNotFoundException(Exception):
    """Raised when a secret cannot be found in the provider."""


class PermissionDeniedException(Exception):
    """Raised when the caller has no permission to access the secret."""


class SecretsManager:
    """Wrapper responsible for retrieving and storing acquirer credentials."""

    def __init__(self, region: str = "us-east-1") -> None:
        self._client = boto3.client("secretsmanager", region_name=region)
        self._cache: Dict[str, Dict[str, str]] = {}

    async def get_acquirer_credentials(
        self, tenant_id: str, acquirer: str
    ) -> Dict[str, str]:
        cache_key = f"{tenant_id}:{acquirer}"
        if cache_key in self._cache:
            logger.debug(
                "credentials_cache_hit", tenant_id=tenant_id, acquirer=acquirer
            )
            return self._cache[cache_key]

        secret_name = f"conciliaai/{tenant_id}/acquirers/{acquirer}"

        try:
            response = self._client.get_secret_value(SecretId=secret_name)
        except self._client.exceptions.ResourceNotFoundException as exc:
            logger.error(
                "credentials_not_found", tenant_id=tenant_id, acquirer=acquirer
            )
            raise SecretNotFoundException(str(exc)) from exc
        except self._client.exceptions.AccessDeniedException as exc:
            logger.error(
                "credentials_access_denied", tenant_id=tenant_id, acquirer=acquirer
            )
            raise PermissionDeniedException(str(exc)) from exc
        except ClientError as exc:
            logger.error(
                "credentials_fetch_failed", tenant_id=tenant_id, acquirer=acquirer, error=str(exc)
            )
            raise

        secret_string = response.get("SecretString")
        if not secret_string:
            logger.error("secret_string_missing", secret=secret_name)
            raise SecretNotFoundException(
                f"Credentials for {tenant_id}:{acquirer} are empty"
            )

        credentials = json.loads(secret_string)
        self._cache[cache_key] = credentials

        logger.info(
            "credentials_fetched",
            tenant_id=tenant_id,
            acquirer=acquirer,
            version=response.get("VersionId"),
        )
        return credentials

    async def store_acquirer_credentials(
        self, tenant_id: str, acquirer: str, credentials: Dict[str, str]
    ) -> None:
        secret_name = f"conciliaai/{tenant_id}/acquirers/{acquirer}"

        try:
            self._client.put_secret_value(
                SecretId=secret_name, SecretString=json.dumps(credentials)
            )
        except self._client.exceptions.ResourceNotFoundException:
            self._client.create_secret(
                Name=secret_name,
                Description=f"Credentials for {tenant_id} and {acquirer}",
                SecretString=json.dumps(credentials),
                Tags=[
                    {"Key": "tenant_id", "Value": tenant_id},
                    {"Key": "acquirer", "Value": acquirer},
                ],
            )
        except ClientError as exc:
            logger.error(
                "credentials_store_failed",
                tenant_id=tenant_id,
                acquirer=acquirer,
                error=str(exc),
            )
            raise
        else:
            logger.info(
                "credentials_stored",
                tenant_id=tenant_id,
                acquirer=acquirer,
            )

        self.invalidate_cache(tenant_id)

    def invalidate_cache(self, tenant_id: Optional[str] = None) -> None:
        if tenant_id is None:
            self._cache.clear()
            logger.info("credentials_cache_invalidated", scope="all")
            return

        keys = [key for key in self._cache if key.startswith(f"{tenant_id}:")]
        for key in keys:
            del self._cache[key]
        logger.info("credentials_cache_invalidated", tenant_id=tenant_id)


__all__ = [
    "SecretsManager",
    "SecretNotFoundException",
    "PermissionDeniedException",
]
