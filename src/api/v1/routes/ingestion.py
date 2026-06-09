"""Routes for ingestion workflows."""

from __future__ import annotations

import tempfile
from datetime import date
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import (
    get_current_tenant,
    get_db_session,
    get_ingestion_service,
    get_rede_api_client,
    require_roles,
)
from src.application.services import IngestionService
from src.domain.entities import Tenant
from src.infrastructure.acquirers import RedeAPIClient, TORCValidationError
from src.infrastructure.persistence.repositories.postgresql_transaction_repository import (
    PostgreSQLTransactionRepository,
)

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


@router.post(
    "/ingestion/rede-api",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Fetch Rede transactions from the REST API",
)
async def ingest_rede_api(
    start_date: date = Query(..., description="Data inicial (YYYY-MM-DD)"),
    end_date: date = Query(..., description="Data final (YYYY-MM-DD)"),
    tenant: Tenant = Depends(get_current_tenant),
    _: dict = Depends(require_roles(["analyst", "admin", "manager"])),
    client: RedeAPIClient = Depends(get_rede_api_client),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Fetch transactions from Rede's REST API and persist them for the tenant.

    Requires REDE_API_BASE_URL/REDE_CLIENT_ID/REDE_CLIENT_SECRET (otherwise 503).
    The HTTP contract is provisional — see ``RedeAPIClient``; if Rede's real
    endpoints/fields differ, adjust the client (paths are env-configurable).
    """
    transactions = await client.fetch_transactions(tenant.id, start_date, end_date)
    repository = PostgreSQLTransactionRepository(session)
    for transaction in transactions:
        await repository.save(transaction)
    await session.commit()
    return {"imported": len(transactions)}
