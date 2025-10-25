"""Bank statement transaction entity."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4


@dataclass(slots=True)
class BankTransaction:
    """Represents a transaction imported from a bank statement (OFX)."""

    id: UUID
    tenant_id: str
    bank_account_id: str
    bank_transaction_id: str
    transaction_date: datetime
    amount: Decimal
    type: str
    memo: str
    description_user_friendly: str
    check_number: str
    is_reconciled: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)

    @staticmethod
    def create(
        tenant_id: str,
        bank_account_id: str,
        bank_transaction_id: str,
        transaction_date: datetime,
        amount: Decimal,
        type: str,
        memo: str,
        description_user_friendly: str,
        check_number: str | None = "",
    ) -> "BankTransaction":
        """Create a new bank transaction instance."""
        return BankTransaction(
            id=uuid4(),
            tenant_id=tenant_id,
            bank_account_id=bank_account_id,
            bank_transaction_id=bank_transaction_id,
            transaction_date=transaction_date,
            amount=amount,
            type=type,
            memo=memo,
            description_user_friendly=description_user_friendly,
            check_number=check_number or "",
        )


__all__ = ["BankTransaction"]
