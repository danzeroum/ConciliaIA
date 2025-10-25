"""Parser for the Cielo Conciliator Agiliza CSV exports."""

from __future__ import annotations

import csv
import io
import re
from datetime import datetime, time
from decimal import Decimal
from typing import Dict, List

from src.domain.value_objects import Acquirer, InstallmentPlan

from .base_parser import BaseAcquirerParser


def _normalise_header(header: str) -> str:
    """Normalise header names from the Agiliza export.

    The files produced by Cielo frequently change between releases and may use
    accented characters or additional whitespace.  The normalisation step keeps
    the parser resilient by reducing the header to a predictable snake_case
    representation.
    """

    slug = re.sub(r"[^\w]+", "_", header.strip().lower())
    slug = re.sub(r"_{2,}", "_", slug)
    return slug.strip("_")


def _parse_decimal(value: str | None) -> Decimal | None:
    if value is None:
        return None
    cleaned = value.strip()
    if not cleaned:
        return None
    cleaned = cleaned.replace(".", "").replace(",", ".")
    return Decimal(cleaned)


def _parse_percentage(value: str | None) -> Decimal | None:
    if value is None:
        return None
    cleaned = value.replace("%", "")
    decimal_value = _parse_decimal(cleaned)
    if decimal_value is None:
        return None
    return (decimal_value / Decimal("100")).quantize(Decimal("0.0001"))


class CieloAgilizaParser(BaseAcquirerParser):
    """Convert CSV rows from the Cielo Conciliator portal into transactions."""

    FIELD_ALIASES = {
        "nsu": {"nsu", "nsu_da_transacao", "nsu_transacao"},
        "authorization_code": {"codigo_de_autorizacao", "cod_autorizacao", "autorizacao"},
        "transaction_date": {"data_da_venda", "data_transacao", "data_da_transacao"},
        "transaction_time": {"hora_da_venda", "hora_transacao"},
        "settlement_date": {"data_pagamento", "data_prevista_pagamento"},
        "gross_amount": {"valor_bruto", "valor_da_venda", "valor_bruto_transacao"},
        "net_amount": {"valor_liquido", "valor_recebido", "valor_liquido_transacao"},
        "mdr_rate": {"taxa_mdr", "taxa_administracao", "taxa"},
        "mdr_amount": {"valor_taxa", "valor_taxas", "valor_desconto"},
        "card_brand": {"bandeira", "bandeira_cartao"},
        "card_last_4": {"ultimos_digitos", "ultimos4", "final_cartao"},
        "installments": {"quantidade_parcelas", "total_parcelas", "parcelas"},
        "installment_number": {"numero_parcela", "parcela_atual"},
        "status": {"status", "status_transacao"},
    }

    def __init__(self) -> None:
        super().__init__(Acquirer.CIELO)

    def _parse_raw_data(self, raw_data: str | bytes | Dict | List[Dict]) -> List[Dict]:
        if isinstance(raw_data, bytes):
            raw_data = raw_data.decode("utf-8")

        if isinstance(raw_data, (dict, list)):
            if isinstance(raw_data, dict):
                return [raw_data]
            return list(raw_data)

        if not isinstance(raw_data, str):
            raise TypeError("raw_data must be a CSV string, dict or list of dicts")

        csv_content = raw_data.strip()
        if not csv_content:
            return []

        reader = csv.DictReader(io.StringIO(csv_content), delimiter=";")
        if reader.fieldnames is None:
            raise ValueError("CSV header ausente no arquivo da Cielo")

        normalised_headers = [_normalise_header(header) for header in reader.fieldnames]
        records: List[Dict] = []
        for row in reader:
            normalised_row = {
                normalised_headers[index]: value.strip() if isinstance(value, str) else value
                for index, value in enumerate(row.values())
            }
            records.append(normalised_row)
        return records

    def _validate_data(self, records: List[Dict]) -> List[Dict]:
        required_fields = {"nsu", "transaction_date", "gross_amount"}
        valid_records: List[Dict] = []

        for record in records:
            if not record:
                continue

            mapped = self._map_aliases(record)

            if not required_fields.issubset(mapped.keys()):
                self.logger.debug("record_missing_fields", record=record)
                continue

            gross_value = _parse_decimal(mapped.get("gross_amount"))
            if gross_value is None or gross_value <= 0:
                self.logger.debug("record_invalid_amount", record=record)
                continue

            try:
                self._parse_date(mapped["transaction_date"])
            except ValueError:
                self.logger.debug("record_invalid_transaction_date", record=record)
                continue

            valid_records.append(mapped)

        return valid_records

    def _normalize_to_canonical(self, record: Dict) -> Dict:
        gross_amount = _parse_decimal(record.get("gross_amount"))
        net_amount = _parse_decimal(record.get("net_amount"))
        mdr_amount = _parse_decimal(record.get("mdr_amount"))
        mdr_rate = _parse_percentage(record.get("mdr_rate"))

        transaction_date = self._parse_date(record["transaction_date"]).date()
        settlement_date = record.get("settlement_date")
        settlement_date_value = (
            self._parse_date(settlement_date).date() if settlement_date else None
        )

        card_last_4 = record.get("card_last_4") or None
        if card_last_4:
            card_last_4 = card_last_4[-4:]

        installments = self._parse_int(record.get("installments"))
        installment_number = self._parse_int(record.get("installment_number"))
        status = record.get("status") or "approved"
        if isinstance(status, str):
            status = status.lower()

        transaction_time_value = None
        transaction_time = record.get("transaction_time")
        if transaction_time:
            try:
                transaction_time_value = self._parse_time(transaction_time)
            except ValueError:
                self.logger.debug("invalid_transaction_time", value=transaction_time)

        canonical = {
            "nsu": record["nsu"],
            "authorization_code": record.get("authorization_code") or None,
            "amount": str(gross_amount),
            "transaction_date": transaction_date,
            "settlement_date": settlement_date_value,
            "card_brand": (record.get("card_brand") or "").lower() or None,
            "card_last_4": card_last_4,
            "mdr_rate": str(mdr_rate) if mdr_rate is not None else None,
            "mdr_amount": str(mdr_amount) if mdr_amount is not None else None,
            "net_amount": str(net_amount) if net_amount is not None else None,
            "status": status,
        }

        if installments:
            canonical["total_installments"] = installments
        if installment_number:
            canonical["current_installment"] = installment_number

        if transaction_time_value:
            canonical["transaction_time"] = transaction_time_value

        return canonical

    def _create_transaction(self, canonical: Dict, tenant_id: str):
        transaction = super()._create_transaction(canonical, tenant_id)

        settlement_date = canonical.get("settlement_date")
        if settlement_date:
            transaction.settlement_date = settlement_date

        transaction_time = canonical.get("transaction_time")
        if transaction_time:
            transaction.transaction_time = transaction_time

        total_installments = canonical.get("total_installments")
        current_installment = canonical.get("current_installment")
        if total_installments and current_installment:
            try:
                installment_amount = transaction.amount / int(total_installments)
                transaction.installment_plan = InstallmentPlan(
                    current_installment=int(current_installment),
                    total_installments=int(total_installments),
                    installment_amount=installment_amount,
                )
            except Exception:
                self.logger.debug(
                    "installment_plan_creation_failed",
                    total=total_installments,
                    current=current_installment,
                )

        return transaction

    def _map_aliases(self, record: Dict) -> Dict:
        mapped: Dict[str, str] = {}
        for key, value in record.items():
            if value is None or (isinstance(value, str) and not value.strip()):
                continue
            mapped_key = None
            for canonical, aliases in self.FIELD_ALIASES.items():
                if key == canonical or key in aliases:
                    mapped_key = canonical
                    break
            if mapped_key is None:
                mapped_key = key
            mapped[mapped_key] = value
        return mapped

    def _parse_date(self, value: str) -> datetime:
        value = value.strip()
        for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y"):
            try:
                return datetime.strptime(value, fmt)
            except ValueError:
                continue
        raise ValueError(f"Data inválida: {value}")

    def _parse_time(self, value: str) -> time:
        value = value.strip()
        for fmt in ("%H:%M:%S", "%H:%M"):
            try:
                return datetime.strptime(value, fmt).time()
            except ValueError:
                continue
        raise ValueError(f"Hora inválida: {value}")

    def _parse_int(self, value: str | None) -> int | None:
        if value is None:
            return None
        cleaned = value.strip()
        if not cleaned:
            return None
        try:
            return int(cleaned)
        except ValueError:
            return None


__all__ = ["CieloAgilizaParser"]
