"""Cielo EDI SFTP client for downloading files."""

from __future__ import annotations

import asyncio
from datetime import date, timedelta
from pathlib import Path
from typing import List

import paramiko
import structlog

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
    ) -> None:
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.ec_number = ec_number
        self.remote_path = remote_path
        self.logger = logger.bind(client="CieloEDIClient", ec_number=ec_number)

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


__all__ = ["CieloEDIClient"]
