"""Utility to parse OFX bank statements into domain-friendly dictionaries."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Dict, List
from xml.etree import ElementTree as ET

import structlog

logger = structlog.get_logger(__name__)


class OFXParser:
    """Parse OFX 1.x (SGML) and 2.x (XML) bank statement payloads."""

    def parse(self, ofx_content: str) -> List[Dict[str, object]]:
        """Parse the raw OFX content and return normalised transactions."""
        content = ofx_content.strip()
        if not content:
            raise ValueError("OFX content is empty")

        if content.startswith("<?xml"):
            return self._parse_ofx_v2(content)
        return self._parse_ofx_v1(content)

    def _parse_ofx_v2(self, xml_content: str) -> List[Dict[str, object]]:
        """Parse OFX 2.x XML payloads."""
        try:
            # Remove xmlns attributes that can break simple XPath queries
            xml_content = xml_content.replace("xmlns=", "xmlnsremoved=")
            root = ET.fromstring(xml_content)
        except ET.ParseError as exc:  # pragma: no cover - defensive logging
            logger.error("ofx_parse_v2_failed", error=str(exc))
            raise ValueError("Arquivo OFX inválido ou corrompido") from exc

        transactions: List[Dict[str, object]] = []
        for stmttrn in root.findall(".//STMTTRN"):
            transaction = self._extract_transaction_from_xml(stmttrn)
            if transaction:
                transactions.append(transaction)

        logger.info("ofx_v2_parsed", transactions=len(transactions))
        return transactions

    def _parse_ofx_v1(self, sgml_content: str) -> List[Dict[str, object]]:
        """Parse OFX 1.x SGML-like payloads."""
        transactions: List[Dict[str, object]] = []
        current_txn: Dict[str, str] = {}
        in_transaction = False

        for raw_line in sgml_content.splitlines():
            line = raw_line.strip()
            if not line:
                continue

            if "<STMTTRN>" in line:
                in_transaction = True
                current_txn = {}
                continue

            if "</STMTTRN>" in line:
                in_transaction = False
                if current_txn:
                    transactions.append(self._normalise_transaction(current_txn))
                current_txn = {}
                continue

            if in_transaction and line.startswith("<") and ":" in line:
                tag, value = line.split(":", 1)
                clean_tag = tag.replace("<", "").replace(">", "")
                current_txn[clean_tag] = value.strip()

        logger.info("ofx_v1_parsed", transactions=len(transactions))
        return transactions

    def _extract_transaction_from_xml(self, stmttrn: ET.Element) -> Dict[str, object]:
        """Convert an XML STMTTRN node into a transaction dictionary."""
        raw_txn = {
            "TRNTYPE": stmttrn.findtext("TRNTYPE", default=""),
            "DTPOSTED": stmttrn.findtext("DTPOSTED", default=""),
            "TRNAMT": stmttrn.findtext("TRNAMT", default="0"),
            "FITID": stmttrn.findtext("FITID", default=""),
            "MEMO": stmttrn.findtext("MEMO", default=""),
            "CHECKNUM": stmttrn.findtext("CHECKNUM", default=""),
        }
        return self._normalise_transaction(raw_txn)

    def _normalise_transaction(self, raw_txn: Dict[str, str]) -> Dict[str, object]:
        """Normalise OFX transaction data into a structured dictionary."""
        date_str = raw_txn.get("DTPOSTED", "")
        transaction_date = self._parse_ofx_date(date_str)

        amount = self._parse_amount(raw_txn.get("TRNAMT", "0"))
        trntype = raw_txn.get("TRNTYPE", "OTHER").upper()

        transaction_type = {
            "CREDIT": "Crédito",
            "DEBIT": "Débito",
            "DEP": "Depósito",
            "XFER": "Transferência",
            "PAYMENT": "Pagamento",
            "OTHER": "Outro",
        }.get(trntype, "Outro")

        memo = raw_txn.get("MEMO", "")
        description = self._build_user_friendly_description(transaction_type, amount, memo)

        return {
            "bank_transaction_id": raw_txn.get("FITID", ""),
            "transaction_date": transaction_date,
            "amount": amount,
            "type": transaction_type,
            "memo": memo,
            "description_user_friendly": description,
            "check_number": raw_txn.get("CHECKNUM", ""),
        }

    def _parse_ofx_date(self, value: str) -> datetime:
        if len(value) >= 8:
            try:
                return datetime.strptime(value[:8], "%Y%m%d")
            except ValueError:  # pragma: no cover - fallback branch
                logger.warning("ofx_invalid_date", raw=value)
        return datetime.utcnow()

    def _parse_amount(self, value: str) -> Decimal:
        try:
            return Decimal(value)
        except Exception:  # pragma: no cover - fallback branch
            logger.warning("ofx_invalid_amount", raw=value)
            return Decimal("0")

    def _build_user_friendly_description(
        self, transaction_type: str, amount: Decimal, memo: str
    ) -> str:
        amount_abs = abs(amount)
        amount_str = f"R$ {amount_abs:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

        prefix = "Crédito" if amount >= 0 else "Débito"
        detail = memo if memo else transaction_type
        return f"{prefix} de {amount_str} - {detail}"


__all__ = ["OFXParser"]
