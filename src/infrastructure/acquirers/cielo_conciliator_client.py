"""HTTP client for interacting with the Cielo Conciliator API."""

from __future__ import annotations

import os
from datetime import date, datetime, timedelta
from typing import Any, Optional

import httpx
import structlog


class CieloConciliatorError(RuntimeError):
    """Raised when the Cielo Conciliator API responds with an error."""


class CieloConciliatorClient:
    """Small HTTP wrapper around the Cielo Conciliator endpoints."""

    def __init__(
        self,
        *,
        base_url: str | None = None,
        client_id: str | None = None,
        client_secret: str | None = None,
        scope: str | None = None,
        timeout: float | None = None,
        http_client: httpx.AsyncClient | None = None,
        token_path: str = "/oauth/token",
        report_path: str = "/conciliator/agiliza/reports",
    ) -> None:
        env_base = base_url or os.getenv("CIELO_CONCILIATOR_BASE_URL")
        if not env_base:
            raise ValueError("CIELO_CONCILIATOR_BASE_URL não configurado")

        env_client_id = client_id or os.getenv("CIELO_CONCILIATOR_CLIENT_ID")
        env_client_secret = client_secret or os.getenv("CIELO_CONCILIATOR_CLIENT_SECRET")
        if not env_client_id or not env_client_secret:
            raise ValueError(
                "Credenciais da Cielo Conciliator ausentes. Defina as variáveis de ambiente "
                "CIELO_CONCILIATOR_CLIENT_ID e CIELO_CONCILIATOR_CLIENT_SECRET."
            )

        self._base_url = env_base.rstrip("/")
        self._client_id = env_client_id
        self._client_secret = env_client_secret
        self._scope = scope or os.getenv("CIELO_CONCILIATOR_SCOPE", "conciliator.read")
        self._token_path = token_path
        self._report_path = report_path
        self._owns_client = http_client is None
        timeout_config = timeout or float(os.getenv("CIELO_CONCILIATOR_TIMEOUT", "30"))
        self._http_client = http_client or httpx.AsyncClient(
            base_url=self._base_url, timeout=timeout_config
        )

        self._logger = structlog.get_logger(__name__).bind(service="CieloConciliatorClient")
        self._token: Optional[str] = None
        self._token_expiry: Optional[datetime] = None

    async def aclose(self) -> None:
        if self._owns_client:
            await self._http_client.aclose()

    async def __aenter__(self) -> "CieloConciliatorClient":  # pragma: no cover - sugar
        return self

    async def __aexit__(self, *_exc_info: Any) -> None:  # pragma: no cover - sugar
        await self.aclose()

    async def download_agiliza_report(
        self, *, start_date: date, end_date: date | None = None
    ) -> str:
        """Download the Agiliza CSV report for the provided interval."""

        if end_date and end_date < start_date:
            raise ValueError("Data final não pode ser anterior à data inicial")

        token = await self._get_token()
        params = {
            "start_date": start_date.isoformat(),
            "end_date": (end_date or start_date).isoformat(),
        }

        headers = {"Authorization": f"Bearer {token}"}

        response = await self._http_client.get(self._report_path, params=params, headers=headers)
        if response.status_code == 204:
            return ""
        if response.status_code >= 400:
            self._logger.error(
                "cielo_conciliator_report_failed",
                status=response.status_code,
                body=response.text,
            )
            raise CieloConciliatorError(
                f"Falha ao baixar relatório da Cielo (status {response.status_code})"
            )

        content_type = response.headers.get("content-type", "")
        if "csv" not in content_type and "text" not in content_type:
            raise CieloConciliatorError("Resposta inesperada da Cielo Conciliator")

        return response.text

    async def _get_token(self) -> str:
        if self._token and self._token_expiry and datetime.utcnow() < self._token_expiry:
            return self._token

        payload = {
            "grant_type": "client_credentials",
            "client_id": self._client_id,
            "client_secret": self._client_secret,
        }
        if self._scope:
            payload["scope"] = self._scope

        response = await self._http_client.post(self._token_path, data=payload)
        if response.status_code >= 400:
            self._logger.error(
                "cielo_conciliator_auth_failed",
                status=response.status_code,
                body=response.text,
            )
            raise CieloConciliatorError("Falha na autenticação com a Cielo Conciliator")

        token_payload = response.json()
        token = token_payload.get("access_token")
        if not token:
            raise CieloConciliatorError("Resposta sem access_token da Cielo Conciliator")

        expires_in = token_payload.get("expires_in", 900)
        try:
            expiry_seconds = int(expires_in)
        except (TypeError, ValueError):  # pragma: no cover - defensive
            expiry_seconds = 900

        self._token = token
        self._token_expiry = datetime.utcnow() + timedelta(seconds=max(expiry_seconds - 60, 60))
        return token


__all__ = ["CieloConciliatorClient", "CieloConciliatorError"]
