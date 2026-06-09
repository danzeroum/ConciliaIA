"""Client for Rede's "Gestão de Vendas" REST API (OAuth2 Basic + Bearer).

Request contract verified against Rede's official Postman collection / docs:

  Token:  POST {base}/oauth2/token
          - HTTP Basic Auth (username=client_id, password=client_secret)
          - form-urlencoded body: grant_type=client_credentials
  Sales:  GET  {base}/merchant-statement/v1/sales
          - Authorization: Bearer <access_token>
          - query: parentCompanyNumber, subsidiaries, startDate, endDate, size
                   (optional: brands, modalities, status)

Env configuration:
  REDE_API_BASE_URL            sandbox:    https://rl7-sandbox-api.useredecloud.com.br
                               production: https://api.userede.com.br/redelabs
  REDE_CLIENT_ID / REDE_CLIENT_SECRET
  REDE_PARENT_COMPANY_NUMBER   merchant / point-of-sale number (sandbox: 13381369)
  REDE_SUBSIDIARIES            defaults to REDE_PARENT_COMPANY_NUMBER
  REDE_SCOPE                   optional OAuth scope
  REDE_TOKEN_PATH              default /oauth2/token
  REDE_SALES_PATH              default /merchant-statement/v1/sales

NOTE — the *response* field mapping in :meth:`_parse_transactions` is still
provisional: Rede's sales response schema (Object Sale) lives behind the
authenticated swagger. Call the import endpoint with ``preview=true`` to capture
a real response and finalize the field names.
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
    """Retrieve sales from Rede's Gestão de Vendas API (OAuth2 client credentials)."""

    def __init__(
        self,
        *,
        base_url: Optional[str] = None,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        parent_company_number: Optional[str] = None,
        subsidiaries: Optional[str] = None,
        token_path: Optional[str] = None,
        sales_path: Optional[str] = None,
        scope: Optional[str] = None,
    ) -> None:
        self.base_url = (base_url or os.getenv("REDE_API_BASE_URL") or "").rstrip("/")
        self.client_id = client_id or os.getenv("REDE_CLIENT_ID")
        self.client_secret = client_secret or os.getenv("REDE_CLIENT_SECRET")
        self.parent_company_number = parent_company_number or os.getenv("REDE_PARENT_COMPANY_NUMBER")
        self.subsidiaries = subsidiaries or os.getenv("REDE_SUBSIDIARIES") or self.parent_company_number
        self.token_path = token_path or os.getenv("REDE_TOKEN_PATH") or "/oauth2/token"
        self.sales_path = sales_path or os.getenv("REDE_SALES_PATH") or "/merchant-statement/v1/sales"
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

        data: Dict[str, str] = {"grant_type": "client_credentials"}
        if self.scope:
            data["scope"] = self.scope
        auth = aiohttp.BasicAuth(self.client_id or "", self.client_secret or "")

        timeout = aiohttp.ClientTimeout(total=30)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(
                f"{self.base_url}{self.token_path}", data=data, auth=auth
            ) as response:
                if response.status != 200:
                    detail = await response.text()
                    logger.error("rede_oauth_failed", status=response.status, detail=detail[:500])
                    raise RuntimeError(f"Rede OAuth failed: {response.status}")
                payload = await response.json(content_type=None)

        token = payload.get("access_token")
        if not token:
            raise RuntimeError("Rede OAuth response is missing access_token")
        expires_in = int(payload.get("expires_in", 1500))
        self._token = token
        self._token_expiry = datetime.utcnow() + timedelta(seconds=max(expires_in - 60, 60))
        return token

    async def fetch_sales_page(
        self,
        *,
        parent_company_number: str,
        start_date: date,
        end_date: date,
        size: int = 100,
    ) -> dict:
        """Return the raw JSON of one sales page (for parsing or contract preview)."""
        token = await self._get_token()
        params = {
            "parentCompanyNumber": parent_company_number,
            "subsidiaries": self.subsidiaries or parent_company_number,
            "startDate": start_date.isoformat(),
            "endDate": end_date.isoformat(),
            "size": size,
        }
        timeout = aiohttp.ClientTimeout(total=60)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(
                f"{self.base_url}{self.sales_path}",
                params=params,
                headers={"Authorization": f"Bearer {token}"},
            ) as response:
                if response.status != 200:
                    detail = await response.text()
                    logger.error("rede_sales_failed", status=response.status, detail=detail[:500])
                    raise RuntimeError(f"Rede sales query failed: {response.status}")
                return await response.json(content_type=None)

    async def fetch_transactions(
        self,
        tenant_id: str,
        start_date: date,
        end_date: date,
        parent_company_number: Optional[str] = None,
    ) -> List[AcquirerTransaction]:
        pcn = parent_company_number or self.parent_company_number
        if not pcn:
            raise ValueError("parentCompanyNumber is required (set REDE_PARENT_COMPANY_NUMBER)")
        logger.info(
            "rede_fetch_started",
            tenant_id=tenant_id,
            start_date=str(start_date),
            end_date=str(end_date),
        )
        data = await self.fetch_sales_page(
            parent_company_number=pcn, start_date=start_date, end_date=end_date
        )
        transactions = self._parse_transactions(self._extract_rows(data), tenant_id)
        logger.info(
            "rede_fetch_completed", tenant_id=tenant_id, transactions_count=len(transactions)
        )
        return transactions

    @staticmethod
    def _extract_rows(data: object) -> List[dict]:
        """Pull the list of sale rows out of the (provisional) response wrapper."""
        if isinstance(data, list):
            return data
        if isinstance(data, dict):
            for key in ("content", "sales", "transactions", "data", "items"):
                value = data.get(key)
                if isinstance(value, list):
                    return value
        return []

    def _parse_transactions(
        self, raw_transactions: List[Dict[str, object]], tenant_id: str
    ) -> List[AcquirerTransaction]:
        """Map Rede sale rows to domain transactions (PROVISIONAL field names)."""
        transactions: List[AcquirerTransaction] = []
        for raw in raw_transactions:
            try:
                nsu = str(raw["nsu"])
                transaction_date = date.fromisoformat(str(raw["transactionDate"])[:10])
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
                logger.warning("rede_transaction_parse_failed", error=str(exc))
                continue
        return transactions


__all__ = ["RedeAPIClient"]
