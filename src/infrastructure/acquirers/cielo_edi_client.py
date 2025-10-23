"""Cielo EDI SFTP client for downloading files."""

from __future__ import annotations

import asyncio
from datetime import date, timedelta
from pathlib import Path
from typing import List

import aiohttp

try:  # pragma: no cover - exercised indirectly via tests
    import paramiko  # type: ignore
except ModuleNotFoundError:  # pragma: no cover - fallback for test environment
    class _ParamikoTransportStub:
        """Minimal stub for :mod:`paramiko` Transport when dependency is absent."""

        def __init__(self, *_: object, **__: object) -> None:
            raise ModuleNotFoundError(
                "paramiko is required for SFTP operations but is not installed"
            )

    class _ParamikoSFTPClientStub:
        """Minimal stub for :mod:`paramiko` SFTPClient when dependency is absent."""

        @staticmethod
        def from_transport(*_: object, **__: object) -> "_ParamikoSFTPClientStub":
            raise ModuleNotFoundError(
                "paramiko is required for SFTP operations but is not installed"
            )

    class _ParamikoStub:
        Transport = _ParamikoTransportStub
        SFTPClient = _ParamikoSFTPClientStub

    paramiko = _ParamikoStub()  # type: ignore
import structlog

from src.domain.entities import AcquirerTransaction
from .cielo_edi_parser import CieloEDIParser

logger = structlog.get_logger(__name__)


class CieloEDIClient:
    """Client for downloading Cielo EDI files via SFTP."""

    def __init__(
        self,
        host: str,
        port: int,
        username: str,
        password: str,
        ec_number: str,
        remote_path: str = "/extrato/",
        parser: CieloEDIParser | None = None,
    ) -> None:
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.ec_number = ec_number
        self.remote_path = remote_path
        self.logger = logger.bind(client="CieloEDIClient", ec_number=ec_number)
        self._parser = parser or CieloEDIParser()
        self._api_host = host if host.startswith("http") else f"https://{host}"

    async def download_file(self, target_date: date, local_path: Path) -> Path | None:
        """Download a single EDI file for the provided date."""
        filename = self._generate_filename(target_date)
        remote_file = f"{self.remote_path}{filename}"

        for attempt in range(3):
            try:
                self.logger.info(
                    "download_started", filename=filename, attempt=attempt + 1
                )
                loop = asyncio.get_event_loop()
                file_path = await loop.run_in_executor(
                    None, self._download_sftp, remote_file, local_path / filename
                )
                self.logger.info("download_completed", file_path=str(file_path))
                return file_path
            except FileNotFoundError:
                self.logger.warning("file_not_found", filename=filename)
                return None
            except Exception as exc:
                self.logger.error(
                    "download_failed",
                    filename=filename,
                    attempt=attempt + 1,
                    error=str(exc),
                )
                if attempt < 2:
                    await asyncio.sleep(2**attempt)
                else:
                    raise
        return None

    def _download_sftp(self, remote_file: str, local_file: Path) -> Path:
        transport = paramiko.Transport((self.host, self.port))
        try:
            transport.connect(username=self.username, password=self.password)
            sftp = paramiko.SFTPClient.from_transport(transport)
            local_file.parent.mkdir(parents=True, exist_ok=True)
            sftp.get(remote_file, str(local_file))
            return local_file
        finally:
            transport.close()

    async def download_date_range(
        self, start_date: date, end_date: date, local_path: Path
    ) -> List[Path]:
        files: List[Path] = []
        current = start_date
        while current <= end_date:
            file_path = await self.download_file(current, local_path)
            if file_path:
                files.append(file_path)
            current += timedelta(days=1)

        self.logger.info(
            "batch_download_completed",
            start_date=start_date.isoformat(),
            end_date=end_date.isoformat(),
            files_downloaded=len(files),
        )
        return files

    def _generate_filename(self, target_date: date) -> str:
        date_str = target_date.strftime("%Y%m%d")
        return f"EC{self.ec_number}_{date_str}.txt"

    def _parse_edi(self, edi_content: str, tenant_id: str) -> List[AcquirerTransaction]:
        """Parse raw EDI content into :class:`AcquirerTransaction` instances."""

        return self._parser.parse(edi_content, tenant_id)

    def parse_edi(self, edi_content: str, tenant_id: str) -> List[AcquirerTransaction]:
        """Public wrapper around :meth:`_parse_edi` for external callers."""

        return self._parse_edi(edi_content, tenant_id)

    async def fetch_transactions(
        self, tenant_id: str, start_date: date, end_date: date
    ) -> List[AcquirerTransaction]:
        """Fetch and parse EDI transactions directly from the HTTP API."""

        auth_url = f"{self._api_host.rstrip('/')}/oauth/token"
        transactions_url = f"{self._api_host.rstrip('/')}/edi/transactions"

        timeout = aiohttp.ClientTimeout(total=60)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            self.logger.info("cielo_authentication_started", url=auth_url)
            async with session.post(
                auth_url,
                json={
                    "grant_type": "client_credentials",
                    "client_id": self.username,
                    "client_secret": self.password,
                },
            ) as auth_response:
                if auth_response.status != 200:
                    detail = await auth_response.text()
                    self.logger.error(
                        "cielo_authentication_failed",
                        status=auth_response.status,
                        detail=detail,
                    )
                    raise RuntimeError(
                        f"Cielo authentication failed: {auth_response.status}"
                    )

                payload = await auth_response.json()
                access_token = payload.get("access_token")
                if not access_token:
                    self.logger.error("cielo_missing_access_token")
                    raise RuntimeError("Cielo authentication did not return an access token")

            headers = {"Authorization": f"Bearer {access_token}", "Accept": "text/plain"}
            params = {
                "start_date": start_date.strftime("%Y-%m-%d"),
                "end_date": end_date.strftime("%Y-%m-%d"),
                "ec": self.ec_number,
            }

            self.logger.info(
                "cielo_edi_download_started",
                url=transactions_url,
                tenant_id=tenant_id,
                start=params["start_date"],
                end=params["end_date"],
            )
            async with session.get(
                transactions_url, headers=headers, params=params
            ) as edi_response:
                if edi_response.status != 200:
                    detail = await edi_response.text()
                    self.logger.error(
                        "cielo_edi_download_failed",
                        status=edi_response.status,
                        detail=detail,
                    )
                    raise RuntimeError(
                        f"Cielo EDI download failed: {edi_response.status}"
                    )

                edi_content = await edi_response.text()

        transactions = self.parse_edi(edi_content, tenant_id)
        self.logger.info(
            "cielo_edi_download_completed",
            tenant_id=tenant_id,
            transactions=len(transactions),
        )
        return transactions


__all__ = ["CieloEDIClient"]
