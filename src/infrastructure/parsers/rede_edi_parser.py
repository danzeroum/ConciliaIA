"""Rede EDI parser implementation (EEVC format)."""

from __future__ import annotations

from datetime import date
from decimal import Decimal, InvalidOperation
from typing import List
from uuid import uuid4

import structlog

from src.domain.entities import AcquirerTransaction
from src.domain.value_objects import Acquirer, InstallmentPlan, Money, NSU
from src.infrastructure.parsers.base_parser import BaseEDIParser
from src.infrastructure.parsers.rede_layouts import (
    extract_field,
    get_layout,
    map_card_brand,
)

logger = structlog.get_logger(__name__)


class RedeEDIParser(BaseEDIParser):
    """Parser for Rede EEVC (Extrato Eletrônico de Vendas Crédito) format."""

    def validate(self, content: str) -> bool:
        """Validate Rede EDI file structure."""
        if not content or not content.strip():
            return False

        lines = content.strip().split("\n")
        if not lines:
            return False

        first_line = lines[0]
        if len(first_line) < 2:
            return False

        record_type = first_line[:2].strip()
        if record_type != "00":
            return False

        if "REDE" not in first_line.upper():
            return False

        return True

    def parse(self, content: str, tenant_id: str) -> List[AcquirerTransaction]:
        """Parse Rede EDI file and extract transactions."""
        if not self.validate(content):
            raise ValueError("Invalid Rede EDI file format")

        logger.info("rede_edi_parsing_started", tenant_id=tenant_id)

        lines = content.strip().split("\n")
        transactions: List[AcquirerTransaction] = []
        transaction_cache: dict[str, dict] = {}

        for line_num, line in enumerate(lines, start=1):
            if not line.strip():
                continue

            try:
                record_type = line[:3].strip()

                if record_type == "010":
                    self._process_cv_summary(line, transaction_cache)
                elif record_type == "012":
                    self._process_cv_details(line, transaction_cache)
                elif record_type == "024":
                    self._process_detailed_transaction(line, transaction_cache)
            except Exception as exc:  # pragma: no cover - defensive logging
                logger.warning(
                    "rede_edi_line_parse_failed",
                    line_num=line_num,
                    record_type=line[:3].strip(),
                    error=str(exc),
                )
                continue

        for nsu, data in transaction_cache.items():
            try:
                transaction = self._build_transaction(tenant_id, nsu, data)
                transactions.append(transaction)
            except Exception as exc:  # pragma: no cover - defensive logging
                logger.warning(
                    "rede_transaction_build_failed",
                    nsu=nsu,
                    error=str(exc),
                )

        logger.info(
            "rede_edi_parsing_completed",
            tenant_id=tenant_id,
            transactions_count=len(transactions),
        )

        return transactions

    def _process_cv_summary(self, line: str, cache: dict) -> None:
        layout = get_layout("010")
        if not layout:
            return

        nsu = extract_field(line, "nsu", layout)
        if not nsu:
            return

        cache.setdefault(nsu, {})
        cache[nsu].update(
            {
                "nsu": nsu,
                "sale_date": extract_field(line, "sale_date", layout),
                "installments": extract_field(line, "installments", layout),
                "gross_amount": extract_field(line, "gross_amount", layout),
                "commission_amount": extract_field(line, "commission_amount", layout),
                "net_amount": extract_field(line, "net_amount", layout),
            }
        )

    def _process_cv_details(self, line: str, cache: dict) -> None:
        layout = get_layout("012")
        if not layout:
            return

        nsu = extract_field(line, "nsu", layout)
        if not nsu or nsu not in cache:
            return

        cache[nsu].update(
            {
                "authorization_code": extract_field(line, "authorization_code", layout),
                "card_brand_code": extract_field(line, "card_brand", layout),
                "detail_sale_date": extract_field(line, "sale_date", layout),
            }
        )

    def _process_detailed_transaction(self, line: str, cache: dict) -> None:
        layout = get_layout("024")
        if not layout:
            return

        nsu = extract_field(line, "nsu", layout)
        if not nsu:
            return

        cache.setdefault(nsu, {})
        cache[nsu].setdefault("nsu", nsu)
        cache[nsu].setdefault("sale_date", extract_field(line, "sale_date", layout))

        gross_amount = extract_field(line, "gross_amount", layout)
        if gross_amount:
            cache[nsu].setdefault("gross_amount", gross_amount)

        card_brand_code = extract_field(line, "card_brand_code", layout)
        if card_brand_code:
            cache[nsu]["card_brand_code"] = card_brand_code

        authorization_code = extract_field(line, "authorization_code", layout)
        if authorization_code:
            cache[nsu].setdefault("authorization_code", authorization_code)

    def _build_transaction(
        self,
        tenant_id: str,
        nsu: str,
        data: dict,
    ) -> AcquirerTransaction:
        """Build AcquirerTransaction entity from parsed data."""

        gross_amount = self._to_decimal(data.get("gross_amount", "0"))
        commission_amount = self._to_decimal(data.get("commission_amount", "0"))
        net_amount = self._to_decimal(data.get("net_amount", "0"))

        if gross_amount == Decimal("0") and net_amount > Decimal("0"):
            gross_amount = net_amount
        if net_amount == Decimal("0") and gross_amount > Decimal("0"):
            net_amount = max(gross_amount - commission_amount, Decimal("0"))
        if (
            commission_amount == Decimal("0")
            and gross_amount > net_amount
            and net_amount > Decimal("0")
        ):
            commission_amount = gross_amount - net_amount

        gross_money = Money(gross_amount)
        mdr_money = Money(commission_amount) if commission_amount > Decimal("0") else None

        net_money = None
        if net_amount > Decimal("0") and net_amount < gross_amount:
            net_money = Money(net_amount)

        sale_date_str = data.get("sale_date") or data.get("detail_sale_date") or ""
        transaction_date_str = self.parse_date(sale_date_str, "DDMMYYYY")
        transaction_date = date.fromisoformat(transaction_date_str)

        try:
            installments = int(data.get("installments", "1"))
        except (TypeError, ValueError):
            installments = 1
        if installments < 1:
            installments = 1

        installment_plan = None
        if installments > 1:
            base_money = net_money or gross_money
            try:
                installment_amount = base_money / Decimal(installments)
                installment_plan = InstallmentPlan(
                    current_installment=1,
                    total_installments=installments,
                    installment_amount=installment_amount,
                )
            except Exception:  # pragma: no cover - defensive guard
                installment_plan = None

        card_brand_code = data.get("card_brand_code", "")
        card_brand = map_card_brand(card_brand_code) if card_brand_code else "VISA"

        return AcquirerTransaction(
            id=str(uuid4()),
            tenant_id=tenant_id,
            acquirer=Acquirer.REDE,
            nsu=NSU(nsu),
            amount=gross_money,
            transaction_date=transaction_date,
            authorization_code=data.get("authorization_code"),
            card_brand=card_brand,
            installment_plan=installment_plan,
            mdr_amount=mdr_money,
            net_amount=net_money,
        )

    @staticmethod
    def _to_decimal(amount_str: str | None, is_cents: bool = True) -> Decimal:
        """Parse numeric string to Decimal handling cents representation."""
        if not amount_str:
            return Decimal("0")

        cleaned = amount_str.strip()
        if not cleaned:
            return Decimal("0")

        try:
            value = Decimal(cleaned)
        except (InvalidOperation, ValueError):
            return Decimal("0")

        return value / Decimal("100") if is_cents else value
