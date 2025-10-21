"""Routes exposing data export capabilities."""

from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import get_current_tenant, get_db_session
from src.application.services.export_service import ExportService
from src.application.services.report_service import ReportService
from src.domain.entities import Tenant
from src.infrastructure.persistence.repositories.postgresql_divergence_repository import (
    PostgreSQLDivergenceRepository,
)
from src.infrastructure.persistence.repositories.postgresql_match_repository import (
    PostgreSQLMatchRepository,
)
from src.infrastructure.persistence.repositories.postgresql_sale_repository import (
    PostgreSQLSaleRepository,
)
from src.infrastructure.persistence.repositories.postgresql_transaction_repository import (
    PostgreSQLTransactionRepository,
)

router = APIRouter()


def _get_export_service(session: AsyncSession) -> ExportService:
    sale_repo = PostgreSQLSaleRepository(session)
    transaction_repo = PostgreSQLTransactionRepository(session)
    match_repo = PostgreSQLMatchRepository(session)
    divergence_repo = PostgreSQLDivergenceRepository(session)

    report_service = ReportService(
        sale_repo=sale_repo,
        transaction_repo=transaction_repo,
        match_repo=match_repo,
        divergence_repo=divergence_repo,
    )

    return ExportService(
        sale_repo=sale_repo,
        transaction_repo=transaction_repo,
        match_repo=match_repo,
        divergence_repo=divergence_repo,
        report_service=report_service,
    )


def get_export_service(
    session: AsyncSession = Depends(get_db_session),
) -> ExportService:
    return _get_export_service(session)


@router.get(
    "/export/sales/excel",
    summary="Exportar vendas para Excel",
    description="Gera uma planilha Excel contendo as vendas filtradas do tenant.",
)
async def export_sales_excel(
    tenant: Tenant = Depends(get_current_tenant),
    service: ExportService = Depends(get_export_service),
    start_date: date | None = Query(None, description="Data inicial do filtro"),
    end_date: date | None = Query(None, description="Data final do filtro"),
):
    if start_date and end_date and start_date > end_date:
        raise HTTPException(status_code=400, detail="A data inicial deve ser anterior à final")

    excel_file = await service.export_sales_to_excel(
        tenant_id=tenant.id,
        start_date=start_date,
        end_date=end_date,
    )

    filename = f"vendas_{date.today().isoformat()}.xlsx"

    return StreamingResponse(
        excel_file,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@router.get(
    "/export/reports/accuracy/excel",
    summary="Exportar relatório de accuracy para Excel",
    description="Gera planilha com os indicadores de accuracy do período informado.",
)
async def export_accuracy_report_excel(
    tenant: Tenant = Depends(get_current_tenant),
    service: ExportService = Depends(get_export_service),
    start_date: date = Query(..., description="Data inicial do relatório"),
    end_date: date = Query(..., description="Data final do relatório"),
):
    if start_date > end_date:
        raise HTTPException(status_code=400, detail="A data inicial deve ser anterior à final")

    excel_file = await service.export_accuracy_report_to_excel(
        tenant_id=tenant.id,
        start_date=start_date,
        end_date=end_date,
    )

    filename = f"relatorio_accuracy_{start_date.isoformat()}_{end_date.isoformat()}.xlsx"

    return StreamingResponse(
        excel_file,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@router.get(
    "/export/reports/divergences/excel",
    summary="Exportar relatório de divergências para Excel",
    description="Gera planilha com a análise de divergências identificadas.",
)
async def export_divergence_report_excel(
    tenant: Tenant = Depends(get_current_tenant),
    service: ExportService = Depends(get_export_service),
    start_date: date = Query(..., description="Data inicial do relatório"),
    end_date: date = Query(..., description="Data final do relatório"),
):
    if start_date > end_date:
        raise HTTPException(status_code=400, detail="A data inicial deve ser anterior à final")

    excel_file = await service.export_divergence_report_to_excel(
        tenant_id=tenant.id,
        start_date=start_date,
        end_date=end_date,
    )

    filename = f"relatorio_divergencias_{start_date.isoformat()}_{end_date.isoformat()}.xlsx"

    return StreamingResponse(
        excel_file,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


__all__ = ["router"]
