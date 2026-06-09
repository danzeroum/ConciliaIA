"""Routes for ingestion workflows."""

from __future__ import annotations

import tempfile
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from src.api.dependencies import get_current_tenant, get_ingestion_service, require_roles
from src.application.services import IngestionService
from src.domain.entities import Tenant
from src.infrastructure.acquirers import TORCValidationError

router = APIRouter()

@router.post(
    "/ingestion/rede-torc",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Ingest Rede TORC offline file",
)
async def ingest_rede_torc(
    file: UploadFile = File(...),
    tenant: Tenant = Depends(get_current_tenant),
    _: dict = Depends(require_roles(["analyst", "admin", "manager"])),
    service: IngestionService = Depends(get_ingestion_service),
) -> dict:
    """Upload and ingest a Rede TORC offline file for the tenant."""

    contents = await file.read()
    if not contents:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Arquivo vazio")

    tmp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp:
            tmp.write(contents)
            tmp_path = Path(tmp.name)

        try:
            processed = await service.ingest_rede_torc(tenant.id, tmp_path)
        except TORCValidationError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

        return {"processed": processed}
    finally:
        await file.close()
        if tmp_path and tmp_path.exists():
            tmp_path.unlink()
