"""Rede REST API integration client."""

from __future__ import annotations

from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Tuple

import aiohttp
import structlog

from src.domain.entities import AcquirerTransaction, Money
from src.infrastructure.security import SecretsManager

logger = structlog.get_logger(__name__)


class RedeAPIClient:
    """Client responsible for retrieving transactions from Rede's REST API."""

    BASE_URL = "https://api.userede.com.br/v1"

    def __init__(self, secrets_manager: SecretsManager) -> None:
        self.secrets_manager = secrets_manager
        self._token_cache: Dict[str, Tuple[str, datetime]] = {}

    async def fetch_transactions(
        self, tenant_id: str, start_date: date, end_date: date
    ) -> List[AcquirerTransaction]:
        logger.info(
            "rede_fetch_started",
            tenant_id=tenant_id,
            start_date=str(start_date),
            end_date=str(end_date),
        )

        credentials = await self.secrets_manager.get_acquirer_credentials(tenant_id, "rede")
        token = await self._get_token(tenant_id, credentials)

        page = 1
        transactions: List[AcquirerTransaction] = []
        while True:
            raw_page = await self._fetch_page(token, start_date, end_date, page)
            if not raw_page:
                break

            transactions.extend(self._parse_transactions(raw_page, tenant_id))

            if len(raw_page) < 100:
                break
            page += 1

            if page > 100:  # safety guard against runaway pagination
                logger.warning("rede_pagination_limit_reached", tenant_id=tenant_id)
                break

        logger.info(
            "rede_fetch_completed", tenant_id=tenant_id, transactions_count=len(transactions)
        )
        return transactions

    async def _get_token(self, tenant_id: str, credentials: Dict[str, str]) -> str:
        cached = self._token_cache.get(tenant_id)
        if cached:
            token, expiry = cached
            if datetime.utcnow() < expiry:
                return token

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.BASE_URL}/oauth/token",
                json={
                    "grant_type": "client_credentials",
                    "client_id": credentials["client_id"],
                    "client_secret": credentials["client_secret"],
                },
                timeout=aiohttp.ClientTimeout(total=30),
            ) as response:
                if response.status != 200:
                    logger.error("rede_oauth_failed", status=response.status)
                    raise RuntimeError(f"Rede OAuth failed: {response.status}")

                data = await response.json()
                token = data["access_token"]
                expires_in = int(data.get("expires_in", 3600))
                expiry = datetime.utcnow() + timedelta(seconds=expires_in - 300)
                self._token_cache[tenant_id] = (token, expiry)
                return token

    async def _fetch_page(
        self, token: str, start_date: date, end_date: date, page: int
    ) -> List[Dict[str, object]]:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.BASE_URL}/transactions",
                params={
                    "startDate": start_date.isoformat(),
                    "endDate": end_date.isoformat(),
                    "page": page,
                    "pageSize": 100,
                },
                headers={"Authorization": f"Bearer {token}"},
                timeout=aiohttp.ClientTimeout(total=60),
            ) as response:
                if response.status != 200:
                    logger.error("rede_fetch_page_failed", status=response.status, page=page)
                    return []

                data = await response.json()
                return data.get("transactions", [])  # type: ignore[return-value]

    def _parse_transactions(
        self, raw_transactions: List[Dict[str, object]], tenant_id: str
    ) -> List[AcquirerTransaction]:
        transactions: List[AcquirerTransaction] = []

        for raw in raw_transactions:
            try:
                nsu = str(raw["nsu"])
                transaction_date = date.fromisoformat(str(raw["transactionDate"]))
                settlement_date = date.fromisoformat(str(raw["settlementDate"]))

                transactions.append(
                    AcquirerTransaction(
                        id=f"rede_{nsu}_{transaction_date.isoformat()}",
                        tenant_id=tenant_id,
                        acquirer="rede",
                        nsu=nsu,
                        transaction_date=transaction_date,
                        settlement_date=settlement_date,
                        gross_amount=Money(Decimal(str(raw["grossAmount"]))),
                        mdr_fee=Money(Decimal(str(raw["mdrFee"]))),
                        net_amount=Money(Decimal(str(raw["netAmount"]))),
                        installments=int(raw.get("installments", 1)),
                    )
                )
            except Exception as exc:  # pragma: no cover - defensive parsing
                logger.warning("rede_transaction_parse_failed", nsu=raw.get("nsu"), error=str(exc))
                continue

        return transactions


__all__ = ["RedeAPIClient"]
