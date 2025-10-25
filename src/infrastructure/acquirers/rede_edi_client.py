"""Rede EDI client for downloading fixed-width files via SFTP."""

from __future__ import annotations

import asyncio
from datetime import date
from pathlib import Path
try:  # pragma: no cover - exercised indirectly in integration tests
    import paramiko  # type: ignore
except ModuleNotFoundError:  # pragma: no cover - fallback stub for test environments
    class _ParamikoTransportStub:
        def __init__(self, *_: object, **__: object) -> None:
            raise ModuleNotFoundError(
                "paramiko is required for Rede EDI SFTP operations but is not installed"
            )

    class _ParamikoSFTPClientStub:
        @staticmethod
        def from_transport(*_: object, **__: object) -> "_ParamikoSFTPClientStub":
            raise ModuleNotFoundError(
                "paramiko is required for Rede EDI SFTP operations but is not installed"
            )

    class _ParamikoStub:
        Transport = _ParamikoTransportStub
        SFTPClient = _ParamikoSFTPClientStub

    paramiko = _ParamikoStub()  # type: ignore

import structlog

logger = structlog.get_logger(__name__)


class RedeEDIClient:
    """Client responsible for retrieving Rede EDI positional files."""

    def __init__(
        self,
        sftp_host: str | None = None,
        username: str | None = None,
        password: str | None = None,
        *,
        port: int | None = None,
        remote_path: str = "/",
        base_path: Path | None = None,
    ) -> None:
        if not base_path and (sftp_host is None or username is None or password is None):
            raise ValueError(
                "Provide either a base_path for local files or SFTP credentials for remote access"
            )
        self.sftp_host = sftp_host
        self.username = username
        self.password = password
        self.port = port or 22
        self.remote_path = remote_path.rstrip("/")
        self.base_path = base_path
        self.logger = logger.bind(client="RedeEDIClient", host=sftp_host or "local")

    async def fetch_eevc(self, file_date: date) -> bytes:
        return await self._fetch_file(self._build_filename("EEVC", file_date))

    async def fetch_eevd(self, file_date: date) -> bytes:
        return await self._fetch_file(self._build_filename("EEVD", file_date))

    async def fetch_eefi(self, file_date: date) -> bytes:
        return await self._fetch_file(self._build_filename("EEFI", file_date))

    async def fetch_eesa(self, file_date: date) -> bytes:
        return await self._fetch_file(self._build_filename("EESA", file_date))

    async def _fetch_file(self, filename: str) -> bytes:
        self.logger.info("rede_edi_fetch_started", filename=filename)
        if self.base_path:
            file_path = self.base_path / filename
            if not file_path.exists():
                raise FileNotFoundError(file_path)
            content = await asyncio.get_event_loop().run_in_executor(
                None, file_path.read_bytes
            )
            self.logger.info("rede_edi_fetch_completed", filename=filename)
            return content

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._download_sftp, filename)

    def _download_sftp(self, filename: str) -> bytes:
        if self.sftp_host is None or self.username is None or self.password is None:
            raise ValueError("Missing SFTP configuration for Rede EDI download")
        transport = paramiko.Transport((self.sftp_host, self.port))
        try:
            transport.connect(username=self.username, password=self.password)
            sftp = paramiko.SFTPClient.from_transport(transport)
            remote_file = f"{self.remote_path}/{filename}" if self.remote_path else filename
            with sftp.open(remote_file, "rb") as remote:
                data = remote.read()
            self.logger.info("rede_edi_sftp_completed", filename=filename)
            return data
        finally:
            transport.close()

    def _build_filename(self, prefix: str, file_date: date) -> str:
        return f"{prefix}{file_date.strftime('%Y%m%d')}.txt"


__all__ = ["RedeEDIClient"]
