"""Base parser implementing Template Method pattern."""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date
from decimal import Decimal
from typing import Dict, List
from uuid import uuid4

import structlog

from src.domain.entities import AcquirerTransaction, TransactionStatus
from src.domain.value_objects import Acquirer, Money, Percentage

logger = structlog.get_logger(__name__)


class AcquirerParserError(Exception):
    """Exception raised when parsing fails."""

    pass


class BaseAcquirerParser(ABC):
    """Base parser for acquirer-specific implementations."""

    def __init__(self, acquirer: Acquirer):
        self.acquirer = acquirer
        self.logger = logger.bind(parser=self.__class__.__name__, acquirer=acquirer.value)

    def parse(self, raw_data: str | bytes | Dict | List[Dict], tenant_id: str) -> List[AcquirerTransaction]:
        """Template method for parsing acquirer data."""
        try:
            self.logger.info("parsing_started", tenant_id=tenant_id)

            parsed_records = self._parse_raw_data(raw_data)
            self.logger.debug("raw_data_parsed", records_count=len(parsed_records))

            validated_records = self._validate_data(parsed_records)
            self.logger.debug("data_validated", valid_records=len(validated_records))

            transactions: List[AcquirerTransaction] = []
            for record in validated_records:
                try:
                    canonical = self._normalize_to_canonical(record)
                    transaction = self._create_transaction(canonical, tenant_id)
                    transactions.append(transaction)
                except Exception as exc:  # pragma: no cover - defensive logging
                    self.logger.warning(
                        "record_normalization_failed", record=record, error=str(exc)
                    )

            self.logger.info(
                "parsing_completed",
                tenant_id=tenant_id,
                total_records=len(parsed_records),
                valid_transactions=len(transactions),
            )
            return transactions
        except Exception as exc:  # pragma: no cover - defensive
            self.logger.error("parsing_failed", error=str(exc))
            raise AcquirerParserError(
                f"Failed to parse {self.acquirer.value} data: {str(exc)}"
            ) from exc

    @abstractmethod
    def _parse_raw_data(self, raw_data: str | bytes | Dict | List[Dict]) -> List[Dict]:
        """Parse raw input data."""

    @abstractmethod
    def _validate_data(self, records: List[Dict]) -> List[Dict]:
        """Validate parsed records."""

    @abstractmethod
    def _normalize_to_canonical(self, record: Dict) -> Dict:
        """Normalize a record into canonical representation."""

    def _create_transaction(self, canonical: Dict, tenant_id: str) -> AcquirerTransaction:
        """Instantiate an :class:`AcquirerTransaction` from canonical data."""
        transaction_date = canonical["transaction_date"]
        if isinstance(transaction_date, date) and transaction_date > date.today():
            # Guard against future dates which would be rejected by the entity
            self.logger.warning(
                "future_transaction_date_adjusted",
                transaction_date=transaction_date.isoformat(),
                tenant_id=tenant_id,
            )
            transaction_date = date.today()

        return AcquirerTransaction(
            id=str(uuid4()),
            tenant_id=tenant_id,
            acquirer=self.acquirer,
            nsu=canonical["nsu"],
            amount=Money(Decimal(canonical["amount"])),
            transaction_date=transaction_date,
            authorization_code=canonical.get("authorization_code"),
            card_brand=canonical.get("card_brand"),
            card_last_4=canonical.get("card_last_4"),
            mdr_rate=Percentage(Decimal(canonical["mdr_rate"]))
            if canonical.get("mdr_rate")
            else None,
            mdr_amount=Money(Decimal(canonical["mdr_amount"]))
            if canonical.get("mdr_amount")
            else None,
            net_amount=Money(Decimal(canonical["net_amount"]))
            if canonical.get("net_amount")
            else None,
            status=TransactionStatus(canonical.get("status", TransactionStatus.APPROVED.value)),
        )


__all__ = ["BaseAcquirerParser", "AcquirerParserError"]
