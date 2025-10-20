"""Service layer for acquirer transactions."""

from __future__ import annotations

import csv
import io
from datetime import date
from decimal import Decimal
from typing import Any, Dict
from uuid import uuid4

import structlog

from src.domain.entities import AcquirerTransaction, TransactionStatus
from src.domain.value_objects import Acquirer, Money, Percentage
from src.infrastructure.persistence.repositories import TransactionRepository

logger = structlog.get_logger(__name__)


class TransactionService:
    """Service responsible for acquirer transaction operations."""

    def __init__(self, transaction_repo: TransactionRepository) -> None:
        self.transaction_repo = transaction_repo

    async def create_transaction(
        self,
        tenant_id: str,
        nsu: str,
        acquirer: str,
        amount: float,
        transaction_date: date,
        card_brand: str | None = None,
        authorization_code: str | None = None,
        mdr_rate: float | None = None,
        mdr_amount: float | None = None,
        status: str | None = None,
    ) -> AcquirerTransaction:
        """Create a new acquirer transaction."""
        acquirer_value: Acquirer | str
        try:
            acquirer_value = Acquirer(acquirer.lower())
        except ValueError:
            acquirer_value = acquirer.lower()

        percentage = (
            Percentage(Decimal(str(mdr_rate)) / Decimal("100"))
            if mdr_rate is not None
            else None
        )
        mdr_amount_money = (
            Money(Decimal(str(mdr_amount))) if mdr_amount is not None else None
        )

        status_value = (
            TransactionStatus(status.lower())
            if status is not None
            else TransactionStatus.APPROVED
        )

        transaction = AcquirerTransaction(
            id=str(uuid4()),
            tenant_id=tenant_id,
            acquirer=acquirer_value,
            nsu=nsu,
            amount=Money(Decimal(str(amount))),
            transaction_date=transaction_date,
            authorization_code=authorization_code,
            card_brand=card_brand,
            mdr_rate=percentage,
            mdr_amount=mdr_amount_money,
            status=status_value,
        )

        await self.transaction_repo.save(transaction)
        logger.info(
            "transaction_created", transaction_id=transaction.id, tenant_id=tenant_id
        )
        return transaction

    async def list_transactions(
        self,
        tenant_id: str,
        start_date: date | None = None,
        end_date: date | None = None,
        acquirer: str | None = None,
        matched: bool | None = None,
        nsu: str | None = None,
        page: int = 1,
        page_size: int = 50,
    ) -> Dict[str, Any]:
        """List transactions with optional filtering."""
        start = start_date or date(1970, 1, 1)
        end = end_date or date.today()

        transactions = await self.transaction_repo.find_by_date_range(
            tenant_id=tenant_id,
            start_date=start,
            end_date=end,
        )

        if acquirer:
            lowered = acquirer.lower()
            transactions = [
                txn
                for txn in transactions
                if str(txn.acquirer).lower() == lowered
            ]

        if nsu:
            lowered_nsu = nsu.lower()
            transactions = [
                txn for txn in transactions if lowered_nsu in str(txn.nsu).lower()
            ]

        if matched is not None:
            unmatched_ids = {
                txn.id for txn in await self.transaction_repo.find_unmatched(tenant_id)
            }
            if matched:
                transactions = [txn for txn in transactions if txn.id not in unmatched_ids]
            else:
                transactions = [txn for txn in transactions if txn.id in unmatched_ids]

        total = len(transactions)
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        items = transactions[start_idx:end_idx]

        return {"items": items, "total": total}

    async def get_transaction(
        self, tenant_id: str, transaction_id: str
    ) -> AcquirerTransaction | None:
        """Retrieve a transaction ensuring tenant isolation."""
        return await self.transaction_repo.find_by_id(tenant_id, transaction_id)

    async def delete_transaction(self, tenant_id: str, transaction_id: str) -> bool:
        """Delete a transaction and return whether it existed."""
        transaction = await self.get_transaction(tenant_id, transaction_id)
        if transaction is None:
            return False

        await self.transaction_repo.delete(tenant_id, transaction_id)
        logger.info(
            "transaction_deleted", transaction_id=transaction_id, tenant_id=tenant_id
        )
        return True

    async def import_from_csv(
        self, tenant_id: str, csv_content: str
    ) -> Dict[str, Any]:
        """Import transactions from CSV contents."""
        imported = 0
        failed = 0
        errors: list[dict[str, Any]] = []

        reader = csv.DictReader(io.StringIO(csv_content))
        for index, row in enumerate(reader, start=2):
            try:
                nsu = (row.get("nsu") or "").strip()
                acquirer = (row.get("acquirer") or "").strip()
                amount_raw = (row.get("amount") or "0").strip()
                date_raw = (row.get("transaction_date") or "").strip()
                card_brand = (row.get("card_brand") or None)
                authorization_code = (row.get("authorization_code") or None)
                mdr_rate_raw = row.get("mdr_rate")
                mdr_amount_raw = row.get("mdr_amount")

                if not nsu or not acquirer or not date_raw:
                    raise ValueError("Missing required fields")

                amount = float(amount_raw)
                transaction_date = date.fromisoformat(date_raw)

                mdr_rate = float(mdr_rate_raw) if mdr_rate_raw else None
                mdr_amount = float(mdr_amount_raw) if mdr_amount_raw else None

                await self.create_transaction(
                    tenant_id=tenant_id,
                    nsu=nsu,
                    acquirer=acquirer,
                    amount=amount,
                    transaction_date=transaction_date,
                    card_brand=card_brand,
                    authorization_code=authorization_code,
                    mdr_rate=mdr_rate,
                    mdr_amount=mdr_amount,
                )
                imported += 1
            except Exception as exc:  # pragma: no cover - defensive
                failed += 1
                errors.append({"row": index, "error": str(exc), "data": row})
                logger.warning(
                    "transaction_import_failed_row",
                    tenant_id=tenant_id,
                    row=index,
                    error=str(exc),
                )

        logger.info(
            "transactions_import_completed",
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
        """Export transactions to CSV format."""
        start = start_date or date(1970, 1, 1)
        end = end_date or date.today()

        transactions = await self.transaction_repo.find_by_date_range(
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
                "acquirer",
                "amount",
                "transaction_date",
                "card_brand",
                "authorization_code",
                "mdr_rate",
                "mdr_amount",
                "status",
            ],
        )
        writer.writeheader()

        for txn in transactions:
            writer.writerow(
                {
                    "id": txn.id,
                    "nsu": str(txn.nsu),
                    "acquirer": str(txn.acquirer),
                    "amount": float(txn.amount.amount),
                    "transaction_date": txn.transaction_date.isoformat(),
                    "card_brand": txn.card_brand or "",
                    "authorization_code": str(txn.authorization_code)
                    if getattr(txn, "authorization_code", None)
                    else "",
                    "mdr_rate": txn.mdr_rate.as_percentage()
                    if txn.mdr_rate is not None
                    else "",
                    "mdr_amount": float(txn.mdr_amount.amount)
                    if txn.mdr_amount is not None
                    else "",
                    "status": txn.status.value if hasattr(txn.status, "value") else txn.status,
                }
            )

        logger.info(
            "transactions_exported",
            tenant_id=tenant_id,
            count=len(transactions),
        )
        return output.getvalue()


__all__ = ["TransactionService"]
