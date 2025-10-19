"""Cielo EDI integration client."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import List

import aiohttp
import structlog

from src.domain.entities import AcquirerTransaction, Money
from src.infrastructure.security import SecretsManager

logger = structlog.get_logger(__name__)


class CieloEDIClient:
    """Client responsible for fetching and parsing Cielo CNAB 240 files."""

    EDI_ENDPOINT = "https://edi.cielo.com.br/api/v2/extratos"

    def __init__(self, secrets_manager: SecretsManager) -> None:
        self.secrets_manager = secrets_manager

    async def fetch_transactions(
        self, tenant_id: str, start_date: date, end_date: date
    ) -> List[AcquirerTransaction]:
        logger.info(
            "cielo_fetch_started",
            tenant_id=tenant_id,
            start_date=str(start_date),
            end_date=str(end_date),
        )

        credentials = await self.secrets_manager.get_acquirer_credentials(tenant_id, "cielo")
        auth_token = await self._authenticate(
            merchant_id=credentials["merchant_id"], api_key=credentials["api_key"]
        )
        edi_content = await self._download_edi(auth_token, start_date, end_date)
        transactions = self._parse_edi(edi_content, tenant_id)

        logger.info(
            "cielo_fetch_completed", tenant_id=tenant_id, transactions_count=len(transactions)
        )
        return transactions

    async def _authenticate(self, merchant_id: str, api_key: str) -> str:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://api.cielo.com.br/auth/oauth/v2/token",
                json={
                    "grant_type": "client_credentials",
                    "merchant_id": merchant_id,
                    "client_secret": api_key,
                },
                headers={"Content-Type": "application/json"},
                timeout=aiohttp.ClientTimeout(total=30),
            ) as response:
                if response.status != 200:
                    logger.error(
                        "cielo_auth_failed",
                        status=response.status,
                        error=await response.text(),
                    )
                    raise RuntimeError(f"Cielo authentication failed: {response.status}")

                data = await response.json()
                return data["access_token"]

    async def _download_edi(self, auth_token: str, start_date: date, end_date: date) -> str:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                self.EDI_ENDPOINT,
                params={
                    "data_inicio": start_date.strftime("%Y%m%d"),
                    "data_fim": end_date.strftime("%Y%m%d"),
                    "formato": "cnab240",
                },
                headers={"Authorization": f"Bearer {auth_token}", "Accept": "text/plain"},
                timeout=aiohttp.ClientTimeout(total=60),
            ) as response:
                if response.status != 200:
                    logger.error("cielo_download_failed", status=response.status)
                    raise RuntimeError(f"EDI download failed: {response.status}")

                return await response.text()

    def _parse_edi(self, edi_content: str, tenant_id: str) -> List[AcquirerTransaction]:
        transactions: List[AcquirerTransaction] = []
        lines = edi_content.strip().splitlines()

        for index, line in enumerate(lines):
            if len(line) < 240 or not line or line[0] != "3":
                continue

            try:
                nsu = line[37:50].strip()
                transaction_date_str = line[69:77]
                transaction_date = date(
                    int(transaction_date_str[0:4]),
                    int(transaction_date_str[4:6]),
                    int(transaction_date_str[6:8]),
                )

                settlement_date_str = line[77:85]
                settlement_date = date(
                    int(settlement_date_str[0:4]),
                    int(settlement_date_str[4:6]),
                    int(settlement_date_str[6:8]),
                )

                gross_cents = int(line[99:114])
                mdr_cents = int(line[115:130])
                net_cents = int(line[131:146])

                gross_amount = Money(Decimal(gross_cents) / Decimal("100"))
                mdr_fee = Money(Decimal(mdr_cents) / Decimal("100"))
                net_amount = Money(Decimal(net_cents) / Decimal("100"))

                installments = int(line[147:150])

                transactions.append(
                    AcquirerTransaction(
                        id=f"cielo_{nsu}_{transaction_date_str}",
                        tenant_id=tenant_id,
                        acquirer="cielo",
                        nsu=nsu,
                        transaction_date=transaction_date,
                        settlement_date=settlement_date,
                        gross_amount=gross_amount,
                        mdr_fee=mdr_fee,
                        net_amount=net_amount,
                        installments=installments,
                    )
                )
            except Exception as exc:  # pragma: no cover - defensive parsing
                logger.warning(
                    "cielo_edi_parse_failed",
                    line=index,
                    error=str(exc),
                )
                continue

        return transactions


__all__ = ["CieloEDIClient"]
