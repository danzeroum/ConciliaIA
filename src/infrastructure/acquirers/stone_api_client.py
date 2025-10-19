"""Stone API REST client."""

from __future__ import annotations

from datetime import date
from typing import Dict, List

import httpx
import structlog

logger = structlog.get_logger(__name__)


class StoneAPIClient:
    """Client for Stone REST API."""

    def __init__(self, client_id: str, client_secret: str, stone_code: str) -> None:
        self.client_id = client_id
        self.client_secret = client_secret
        self.stone_code = stone_code
        self.base_url = "https://api.stone.com.br/v1"
        self.access_token: str | None = None
        self.logger = logger.bind(client="StoneAPIClient", stone_code=stone_code)

    async def fetch_transactions(
        self, start_date: date, end_date: date
    ) -> List[Dict]:
        if not self.access_token:
            await self._authenticate()

        transactions: List[Dict] = []
        page = 1
        has_more = True

        async with httpx.AsyncClient(timeout=30.0) as client:
            while has_more:
                try:
                    self.logger.info(
                        "fetching_transactions_page",
                        page=page,
                        start_date=start_date.isoformat(),
                        end_date=end_date.isoformat(),
                    )
                    response = await client.get(
                        f"{self.base_url}/transactions",
                        params={
                            "stone_code": self.stone_code,
                            "start_date": start_date.isoformat(),
                            "end_date": end_date.isoformat(),
                            "page": page,
                            "per_page": 100,
                        },
                        headers={
                            "Authorization": f"Bearer {self.access_token}",
                            "Content-Type": "application/json",
                        },
                    )

                    if response.status_code == 401:
                        await self._authenticate()
                        continue

                    response.raise_for_status()
                    data = response.json()
                    transactions.extend(data.get("transactions", []))
                    pagination = data.get("pagination", {})
                    has_more = bool(pagination.get("has_next"))
                    page += 1
                except httpx.HTTPError as exc:
                    self.logger.error("api_request_failed", page=page, error=str(exc))
                    raise

        self.logger.info("transactions_fetched", total=len(transactions))
        return transactions

    async def _authenticate(self) -> None:
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                self.logger.info("authenticating")
                response = await client.post(
                    f"{self.base_url}/oauth/token",
                    json={
                        "grant_type": "client_credentials",
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                    },
                )
                response.raise_for_status()
                data = response.json()
                self.access_token = data["access_token"]
                self.logger.info("authentication_successful")
            except httpx.HTTPError as exc:
                self.logger.error("authentication_failed", error=str(exc))
                raise


__all__ = ["StoneAPIClient"]
