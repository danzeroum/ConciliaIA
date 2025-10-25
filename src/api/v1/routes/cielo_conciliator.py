"""Routes that expose the Cielo Conciliator integration."""

from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from src.api.dependencies import (
    get_current_tenant,
    get_import_cielo_report_use_case,
)
from src.application.use_cases.cielo_conciliator import (
    ImportCieloReportRequest,
    ImportCieloReportUseCase,
)
from src.domain.entities import Tenant

router = APIRouter(prefix="/cielo-conciliator", tags=["Cielo Conciliator"])


class ImportReportRequest(BaseModel):
    """Payload accepted by the import endpoint."""

    start_date: date = Field(..., description="Data inicial do período a importar")
    end_date: date | None = Field(
        default=None,
        description="Data final (opcional). Quando não informada usa a data inicial.",
    )


class ImportReportResponse(BaseModel):
    imported: int
    message: str


@router.post(
    "/import",
    response_model=ImportReportResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Importar relatório Agiliza da Cielo",
)
async def import_cielo_report(
    payload: ImportReportRequest,
    tenant: Tenant = Depends(get_current_tenant),
    use_case: ImportCieloReportUseCase = Depends(get_import_cielo_report_use_case),
) -> ImportReportResponse:
    """Import a report from the Cielo Conciliator portal."""

    if payload.end_date and payload.end_date < payload.start_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A data final deve ser igual ou posterior à data inicial",
        )

    result = await use_case.execute(
        ImportCieloReportRequest(
            tenant_id=tenant.id,
            start_date=payload.start_date,
            end_date=payload.end_date,
        )
    )

    if result.imported == 0:
        message = "Nenhuma transação encontrada para o período informado."
    elif payload.end_date and payload.end_date != payload.start_date:
        message = (
            f"Importamos {result.imported} transações da Cielo entre "
            f"{payload.start_date:%d/%m/%Y} e {payload.end_date:%d/%m/%Y}."
        )
    else:
        message = (
            f"Importamos {result.imported} transações da Cielo para "
            f"{payload.start_date:%d/%m/%Y}."
        )

    return ImportReportResponse(imported=result.imported, message=message)


__all__ = ["router"]
