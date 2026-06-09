"""Client for Rede's REST sales/conciliation API (OAuth2 + Bearer token).

Configuration is env-driven, mirroring the Cielo Conciliator client:

  REDE_API_BASE_URL        sandbox: https://rl7-sandbox-api.useredecloud.com.br
                           production: https://api.userede.com.br/redelabs
  REDE_CLIENT_ID           OAuth2 client id
  REDE_CLIENT_SECRET       OAuth2 client secret
  REDE_TOKEN_PATH          token endpoint path (default "/oauth/token")
  REDE_TRANSACTIONS_PATH   sales/transactions endpoint path (default "/transactions")
  REDE_SCOPE               optional OAuth scope

NOTE — provisional HTTP contract: the exact token endpoint, grant type and the
sales-query path / response fields of Rede's authenticated "Gestão de Vendas" /
Conciliation API live behind Rede's developer portal. The request and response
mapping below is a best-effort starting point; the base URL, token path and
transactions path are all overridable via the env vars above, and the response
field mapping lives in :meth:`_parse_transactions`. Verify both against your Rede
API documentation and adjust as needed.
"""

from __future__ import annotations

import os
from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional

import aiohttp
import structlog

from src.domain.entities import AcquirerTransaction
from src.domain.value_objects import Money

logger = structlog.get_logger(__name__)


class RedeAPIClient:
    """Retrieve transactions from Rede's REST API via OAuth2 client credentials."""

    def __init__(
        self,
        *,
        base_url: Optional[str] = None,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        token_path: Optional[str] = None,
        transactions_path: Optional[str] = None,
        scope: Optional[str] = None,
    ) -> None:
        self.base_url = (base_url or os.getenv("REDE_API_BASE_URL") or "").rstrip("/")
        self.client_id = client_id or os.getenv("REDE_CLIENT_ID")
        self.client_secret = client_secret or os.getenv("REDE_CLIENT_SECRET")
        self.token_path = token_path or os.getenv("REDE_TOKEN_PATH", "/oauth/token")
        self.transactions_path = transactions_path or os.getenv(
            "REDE_TRANSACTIONS_PATH", "/transactions"
        )
        self.scope = scope or os.getenv("REDE_SCOPE")

        missing = [
            name
            for name, value in (
                ("REDE_API_BASE_URL", self.base_url),
                ("REDE_CLIENT_ID", self.client_id),
                ("REDE_CLIENT_SECRET", self.client_secret),
            )
            if not value
        ]
        if missing:
            raise ValueError("Rede API client is not configured: missing " + ", ".join(missing))

        self._token: Optional[str] = None
        self._token_expiry: Optional[datetime] = None

    async def _get_token(self) -> str:
        if self._token and self._token_expiry and datetime.utcnow() < self._token_expiry:
            return self._token

        payload: Dict[str, str] = {
            "grant_type": "client_credentials",
            "client_id": self.client_id or "",
            "client_secret": self.client_secret or "",
        }
        if self.scope:
            payload["scope"] = self.scope

        timeout = aiohttp.ClientTimeout(total=30)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(f"{self.base_url}{self.token_path}", json=payload) as response:
                if response.status != 200:
                    detail = await response.text()
                    logger.error("rede_oauth_failed", status=response.status, detail=detail[:500])
                    raise RuntimeError(f"Rede OAuth failed: {response.status}")
                data = await response.json()

        token = data.get("access_token")
        if not token:
            raise RuntimeError("Rede OAuth response is missing access_token")
        expires_in = int(data.get("expires_in", 3600))
        self._token = token
        self._token_expiry = datetime.utcnow() + timedelta(seconds=max(expires_in - 300, 60))
        return token

    async def fetch_transactions(
        self, tenant_id: str, start_date: date, end_date: date
    ) -> List[AcquirerTransaction]:
        logger.info(
            "rede_fetch_started",
            tenant_id=tenant_id,
            start_date=str(start_date),
            end_date=str(end_date),
        )
        token = await self._get_token()

        transactions: List[AcquirerTransaction] = []
        page = 1
        timeout = aiohttp.ClientTimeout(total=60)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            while True:
                async with session.get(
                    f"{self.base_url}{self.transactions_path}",
                    params={
                        "startDate": start_date.isoformat(),
                        "endDate": end_date.isoformat(),
                        "page": page,
                        "pageSize": 100,
                    },
                    headers={"Authorization": f"Bearer {token}"},
                ) as response:
                    if response.status != 200:
                        logger.error("rede_fetch_page_failed", status=response.status, page=page)
                        break
                    data = await response.json()

                raw_page = data.get("transactions", []) if isinstance(data, dict) else []
                if not raw_page:
                    break
                transactions.extend(self._parse_transactions(raw_page, tenant_id))
                if len(raw_page) < 100 or page >= 100:  # safety guard
                    break
                page += 1

        logger.info(
            "rede_fetch_completed", tenant_id=tenant_id, transactions_count=len(transactions)
        )
        return transactions

    def _parse_transactions(
        self, raw_transactions: List[Dict[str, object]], tenant_id: str
    ) -> List[AcquirerTransaction]:
        """Map Rede API rows to domain transactions (provisional field names)."""
        transactions: List[AcquirerTransaction] = []
        for raw in raw_transactions:
            try:
                nsu = str(raw["nsu"])
                transaction_date = date.fromisoformat(str(raw["transactionDate"]))
                transactions.append(
                    AcquirerTransaction(
                        id=f"rede_{nsu}_{transaction_date.isoformat()}",
                        tenant_id=tenant_id,
                        acquirer="rede",
                        nsu=nsu,
                        amount=Money(Decimal(str(raw["grossAmount"]))),
                        transaction_date=transaction_date,
                        mdr_amount=Money(Decimal(str(raw["mdrFee"]))),
                        net_amount=Money(Decimal(str(raw["netAmount"]))),
                    )
                )
            except Exception as exc:  # pragma: no cover - defensive parsing
                logger.warning("rede_transaction_parse_failed", nsu=raw.get("nsu"), error=str(exc))
                continue
        return transactions


__all__ = ["RedeAPIClient"]
