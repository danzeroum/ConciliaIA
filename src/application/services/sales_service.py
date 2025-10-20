"""Service layer for sales management."""

from __future__ import annotations

import csv
import io
from datetime import date
from decimal import Decimal
from typing import Any, Dict
from uuid import uuid4

import structlog

from src.domain.entities import Sale
from src.domain.value_objects import Money
from src.infrastructure.persistence.repositories import SaleRepository

logger = structlog.get_logger(__name__)


class SalesService:
    """Service responsible for sales related operations."""

    def __init__(self, sale_repo: SaleRepository) -> None:
        self.sale_repo = sale_repo

    async def create_sale(
        self,
        tenant_id: str,
        nsu: str,
        amount: float,
        sale_date: date,
        payment_method: str,
        installments: int = 1,
        authorization_code: str | None = None,
    ) -> Sale:
        """Create and persist a new sale."""
        sale = Sale(
            id=str(uuid4()),
            tenant_id=tenant_id,
            nsu=nsu,
            amount=Money(Decimal(str(amount))),
            date=sale_date,
            payment_method=payment_method,
            authorization_code=authorization_code,
            installments=installments,
        )

        await self.sale_repo.save(sale)
        logger.info("sale_created", sale_id=sale.id, tenant_id=tenant_id)
        return sale

    async def list_sales(
        self,
        tenant_id: str,
        start_date: date | None = None,
        end_date: date | None = None,
        payment_method: str | None = None,
        matched: bool | None = None,
        nsu: str | None = None,
        page: int = 1,
        page_size: int = 50,
    ) -> Dict[str, Any]:
        """Return a paginated list of sales applying optional filters."""
        start = start_date or date(1970, 1, 1)
        end = end_date or date.today()

        sales = await self.sale_repo.find_by_date_range(
            tenant_id=tenant_id,
            start_date=start,
            end_date=end,
        )

        if payment_method:
            sales = [s for s in sales if s.payment_method == payment_method]

        if nsu:
            lowered = nsu.lower()
            sales = [s for s in sales if lowered in str(s.nsu).lower()]

        if matched is not None:
            unmatched_ids = {
                sale.id for sale in await self.sale_repo.find_unmatched(tenant_id)
            }
            if matched:
                sales = [s for s in sales if s.id not in unmatched_ids]
            else:
                sales = [s for s in sales if s.id in unmatched_ids]

        total = len(sales)
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        items = sales[start_idx:end_idx]

        return {"items": items, "total": total}

    async def get_sale(self, tenant_id: str, sale_id: str) -> Sale | None:
        """Retrieve a sale ensuring tenant isolation."""
        return await self.sale_repo.find_by_id(tenant_id, sale_id)

    async def update_sale(
        self,
        tenant_id: str,
        sale_id: str,
        amount: float | None = None,
        payment_method: str | None = None,
        installments: int | None = None,
        authorization_code: str | None = None,
    ) -> Sale | None:
        """Update mutable fields of a sale."""
        sale = await self.get_sale(tenant_id, sale_id)
        if sale is None:
            return None

        if amount is not None:
            sale.amount = Money(Decimal(str(amount)))
        if payment_method is not None:
            sale.payment_method = payment_method
        if installments is not None:
            sale.installments = installments
        if authorization_code is not None:
            sale.authorization_code = authorization_code

        await self.sale_repo.save(sale)
        logger.info("sale_updated", sale_id=sale_id, tenant_id=tenant_id)
        return sale

    async def delete_sale(self, tenant_id: str, sale_id: str) -> bool:
        """Delete a sale and return whether it existed."""
        sale = await self.get_sale(tenant_id, sale_id)
        if sale is None:
            return False

        await self.sale_repo.delete(tenant_id, sale_id)
        logger.info("sale_deleted", sale_id=sale_id, tenant_id=tenant_id)
        return True

    async def import_from_csv(self, tenant_id: str, csv_content: str) -> Dict[str, Any]:
        """Import multiple sales from CSV contents."""
        imported = 0
        failed = 0
        errors: list[dict[str, Any]] = []

        reader = csv.DictReader(io.StringIO(csv_content))
        for index, row in enumerate(reader, start=2):
            try:
                nsu = (row.get("nsu") or "").strip()
                amount_raw = (row.get("amount") or "0").strip()
                sale_date_raw = (row.get("sale_date") or "").strip()
                payment_method = (row.get("payment_method") or "").strip()
                installments_raw = (row.get("installments") or "1").strip()
                authorization_code = (row.get("authorization_code") or None)

                if not nsu or not sale_date_raw or not payment_method:
                    raise ValueError("Missing required fields")

                amount = float(amount_raw)
                installments = int(installments_raw)

                parsed_date = date.fromisoformat(sale_date_raw)

                await self.create_sale(
                    tenant_id=tenant_id,
                    nsu=nsu,
                    amount=amount,
                    sale_date=parsed_date,
                    payment_method=payment_method,
                    installments=installments,
                    authorization_code=authorization_code,
                )
                imported += 1
            except Exception as exc:  # pragma: no cover - defensive
                failed += 1
                errors.append({"row": index, "error": str(exc), "data": row})
                logger.warning(
                    "sale_import_failed_row",
                    tenant_id=tenant_id,
                    row=index,
                    error=str(exc),
                )

        logger.info(
            "sales_import_completed",
            tenant_id=tenant_id,
            imported=imported,
            failed=failed,
        )
        return {"imported": imported, "failed": failed, "errors": errors}

    async def export_to_csv(
        self,
        tenant_id: str,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> str:
        """Export sales to CSV format."""
        start = start_date or date(1970, 1, 1)
        end = end_date or date.today()

        sales = await self.sale_repo.find_by_date_range(
            tenant_id=tenant_id,
            start_date=start,
            end_date=end,
        )

        output = io.StringIO()
        writer = csv.DictWriter(
            output,
            fieldnames=[
                "id",
                "nsu",
                "amount",
                "sale_date",
                "payment_method",
                "authorization_code",
                "installments",
            ],
        )
        writer.writeheader()

        for sale in sales:
            writer.writerow(
                {
                    "id": sale.id,
                    "nsu": str(sale.nsu),
                    "amount": float(sale.amount.amount),
                    "sale_date": sale.date.isoformat(),
                    "payment_method": sale.payment_method,
                    "authorization_code": str(sale.authorization_code)
                    if getattr(sale, "authorization_code", None)
                    else "",
                    "installments": sale.installments,
                }
            )

        logger.info(
            "sales_exported",
            tenant_id=tenant_id,
            count=len(sales),
        )
        return output.getvalue()


__all__ = ["SalesService"]
