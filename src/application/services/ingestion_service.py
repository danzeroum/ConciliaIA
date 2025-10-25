"""Service for ingesting transactions from acquirers."""

from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path
from typing import Dict

import structlog

from src.domain.value_objects import Acquirer
from src.infrastructure.acquirers import (
    CieloEDIClient,
    CieloEDIParser,
    RedeEDIClient,
    RedeEDIParser,
    StoneAPIClient,
    StoneParser,
)
from src.infrastructure.persistence.repositories import TransactionRepository

logger = structlog.get_logger(__name__)


class IngestionService:
    """Service for ingesting transactions from multiple acquirers."""

    def __init__(self, transaction_repo: TransactionRepository) -> None:
        self.transaction_repo = transaction_repo
        self.logger = logger.bind(service="IngestionService")

    async def ingest_cielo_edi(
        self,
        tenant_id: str,
        client: CieloEDIClient,
        target_date: date,
        local_path: Path,
    ) -> int:
        self.logger.info(
            "cielo_ingestion_started",
            tenant_id=tenant_id,
            target_date=target_date.isoformat(),
        )
        file_path = await client.download_file(target_date, local_path)
        if not file_path:
            self.logger.warning("cielo_file_not_found", target_date=target_date.isoformat())
            return 0

        parser = CieloEDIParser()
        with file_path.open("r", encoding="latin-1") as fh:
            edi_content = fh.read()
        transactions = parser.parse(edi_content, tenant_id)
        for transaction in transactions:
            await self.transaction_repo.save(transaction)

        self.logger.info(
            "cielo_ingestion_completed",
            tenant_id=tenant_id,
            transactions_count=len(transactions),
        )
        return len(transactions)

    async def ingest_rede_edi(
        self,
        tenant_id: str,
        client: RedeEDIClient,
        file_date: date,
        file_type: str = "EEVC",
    ) -> int:
        file_type_upper = file_type.upper()
        self.logger.info(
            "rede_ingestion_started",
            tenant_id=tenant_id,
            file_date=file_date.isoformat(),
            file_type=file_type_upper,
        )

        fetch_map = {
            "EEVC": client.fetch_eevc,
            "EEVD": client.fetch_eevd,
            "EEFI": client.fetch_eefi,
            "EESA": client.fetch_eesa,
        }
        if file_type_upper not in fetch_map:
            raise ValueError(f"Tipo arquivo não suportado: {file_type}")

        try:
            raw_data = await fetch_map[file_type_upper](file_date)
        except FileNotFoundError:
            self.logger.warning(
                "rede_file_not_found",
                file_date=file_date.isoformat(),
                file_type=file_type_upper,
            )
            return 0

        parser = RedeEDIParser()
        transactions = parser.parse(raw_data, tenant_id)
        for transaction in transactions:
            await self.transaction_repo.save(transaction)

        self.logger.info(
            "rede_ingestion_completed",
            tenant_id=tenant_id,
            file_type=file_type_upper,
            transactions_count=len(transactions),
        )
        return len(transactions)

    async def ingest_stone_api(
        self,
        tenant_id: str,
        client: StoneAPIClient,
        start_date: date,
        end_date: date,
    ) -> int:
        self.logger.info(
            "stone_ingestion_started",
            tenant_id=tenant_id,
            start_date=start_date.isoformat(),
            end_date=end_date.isoformat(),
        )
        raw_transactions = await client.fetch_transactions(start_date, end_date)
        parser = StoneParser()
        transactions = parser.parse(raw_transactions, tenant_id)
        for transaction in transactions:
            await self.transaction_repo.save(transaction)

        self.logger.info(
            "stone_ingestion_completed",
            tenant_id=tenant_id,
            transactions_count=len(transactions),
        )
        return len(transactions)

    async def ingest_all_acquirers(
        self,
        tenant_id: str,
        start_date: date,
        end_date: date,
        acquirer_configs: Dict[str, dict],
    ) -> Dict[Acquirer, int]:
        results: Dict[Acquirer, int] = {}

        if "cielo" in acquirer_configs:
            config = acquirer_configs["cielo"]
            client = CieloEDIClient(**config["client_params"])
            local_path = Path(config.get("local_path", "/tmp/cielo"))
            total = 0
            current_date = start_date
            while current_date <= end_date:
                total += await self.ingest_cielo_edi(tenant_id, client, current_date, local_path)
                current_date += timedelta(days=1)
            results[Acquirer.CIELO] = total

        if "rede" in acquirer_configs:
            config = acquirer_configs["rede"]
            client = RedeEDIClient(**config["client_params"])
            file_types = [ft.upper() for ft in config.get("file_types", ["EEVC", "EEVD"])]
            total = 0
            current_date = start_date
            while current_date <= end_date:
                for file_type in file_types:
                    total += await self.ingest_rede_edi(
                        tenant_id, client, current_date, file_type
                    )
                current_date += timedelta(days=1)
            results[Acquirer.REDE] = total

        if "stone" in acquirer_configs:
            config = acquirer_configs["stone"]
            client = StoneAPIClient(**config["client_params"])
            count = await self.ingest_stone_api(tenant_id, client, start_date, end_date)
            results[Acquirer.STONE] = count

        self.logger.info("ingestion_completed", tenant_id=tenant_id, results=results)
        return results


__all__ = ["IngestionService"]
