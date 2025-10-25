"""Rede TORC offline file parser implementation."""

from __future__ import annotations

from datetime import datetime, date
from decimal import Decimal
from typing import Dict, List, Mapping, MutableMapping, Optional, Set

from src.domain.value_objects import Acquirer

from .base_parser import AcquirerParserError, BaseAcquirerParser


class TORCValidationError(Exception):
    """Raised when a TORC file does not comply with the specification."""


class ValidationError(TORCValidationError):
    """Backward compatible alias for validation errors."""


class RedeTORCParser(BaseAcquirerParser):
    """Parse CSV files that follow the Rede TORC offline specification."""

    RECORD_TYPES: Mapping[str, str] = {
        "00": "header",
        "01": "resumo_vendas",
        "02": "total_pv",
        "03": "total_matriz",
        "04": "total_arquivo",
        "05": "detalhe_cv",
        "13": "detalhe_ecommerce",
        "20": "detalhe_recarga",
        "08": "desagendamento",
        "09": "predatadas_liquid",
        "11": "ajuste_net",
        "17": "ajuste_ecomm",
        "18": "negociadas",
        "19": "icplus",
    }

    BRAND_MAPPING: Mapping[str, str] = {
        "0": "outras",
        "1": "maestro",
        "3": "visa_electron",
        "4": "cabal",
        "9": "sicredi",
        "A": "avista",
        "B": "banescard",
        "E": "elo",
        "X": "amex",
    }

    SUPPORTED_BRANDS: Set[str] = {
        "maestro",
        "visa_electron",
        "hiper",
        "cabal",
        "banescard",
        "elo",
        "amex",
    }

    def __init__(self) -> None:
        super().__init__(Acquirer.REDE)

    def parse(
        self, raw_data: str | bytes | Dict | List[Dict], tenant_id: str
    ) -> List:
        try:
            return super().parse(raw_data, tenant_id)
        except AcquirerParserError as exc:
            cause = exc.__cause__
            if isinstance(cause, TORCValidationError):
                raise cause
            raise

    def _parse_raw_data(
        self, raw_data: str | bytes | Dict | List[Dict]
    ) -> List[Dict]:
        if isinstance(raw_data, list):
            return raw_data
        if isinstance(raw_data, dict):
            return [raw_data]
        if isinstance(raw_data, bytes):
            raw_text = raw_data.decode("utf-8")
        else:
            raw_text = raw_data or ""

        lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
        if not lines:
            return []

        records: List[Dict[str, object]] = []
        for position, line in enumerate(lines, start=1):
            parts = line.split(",")
            if not parts:
                continue
            record_type = parts[0]
            handler_name = self.RECORD_TYPES.get(record_type)
            if not handler_name:
                raise TORCValidationError(f"Registro desconhecido: {record_type}")

            parser_method = getattr(self, f"_parse_{handler_name}", None)
            if not callable(parser_method):
                continue

            parsed = parser_method(line)
            parsed["record_sequence"] = position
            records.append(parsed)

        return records

    def _validate_data(self, records: List[Dict]) -> List[Dict]:
        if not records:
            return []

        header = records[0]
        trailer = records[-1]

        if header.get("record_type") != "00":
            raise TORCValidationError("Arquivo TORC sem header válido")

        if trailer.get("record_type") != "04":
            raise TORCValidationError("Arquivo TORC sem trailer válido")

        sequencia = header.get("sequencia")
        processamento = (header.get("processamento") or "").lower()
        if sequencia != "0001" and processamento != "reprocessamento":
            raise TORCValidationError("Sequência movimento deve começar em 0001")

        total_registros = trailer.get("total_registros")
        if total_registros is None:
            raise TORCValidationError("Trailer sem total de registros")

        try:
            total_informado = int(total_registros)
        except ValueError as exc:
            raise TORCValidationError("Total de registros inválido no trailer") from exc

        if total_informado != len(records):
            raise TORCValidationError(
                "Total de registros divergente do informado no trailer"
            )

        detalhes_por_resumo: Dict[str, Dict[str, object]] = {}
        validated_records: List[Dict[str, object]] = []

        for record in records:
            record_type = record.get("record_type")
            if record_type == "05":
                nsu_rv = record.get("nsu_rv")
                if nsu_rv:
                    detalhes_por_resumo.setdefault(str(nsu_rv), {}).update(record)
            elif record_type == "01":
                resumo = record.copy()
                nsu = str(resumo.get("nsu", ""))
                if not nsu:
                    raise TORCValidationError("Resumo de vendas sem NSU")

                card_brand = resumo.get("card_brand")
                if card_brand and card_brand not in self.SUPPORTED_BRANDS:
                    raise TORCValidationError(
                        f"Bandeira não suportada: {card_brand}"
                    )

                detalhe = detalhes_por_resumo.get(nsu)
                if detalhe:
                    resumo.update(
                        {
                            "authorization_code": detalhe.get("autorizacao"),
                            "card_last_4": detalhe.get("cartao_last4"),
                            "capture_type": detalhe.get("tipo_captura"),
                            "terminal": detalhe.get("terminal"),
                            "transaction_time": detalhe.get("hora"),
                        }
                    )
                    compre_saque = detalhe.get("compre_saque") or {}
                    compra = compre_saque.get("valor_compra")
                    saque = compre_saque.get("valor_saque")
                    if compra is not None and saque is not None:
                        resumo["gross_amount"] = (compra + saque).quantize(
                            Decimal("0.01")
                        )

                validated_records.append(resumo)

        return validated_records

    def _normalize_to_canonical(self, record: Dict) -> Dict:
        gross_amount: Decimal = record["gross_amount"]
        discount_amount: Decimal = record.get("discount_amount", Decimal("0"))
        net_amount: Decimal = record.get(
            "net_amount", (gross_amount - discount_amount).quantize(Decimal("0.01"))
        )

        mdr_rate: Optional[Decimal] = None
        if gross_amount and gross_amount != 0:
            mdr_rate = (discount_amount / gross_amount).quantize(Decimal("0.0001"))

        transaction_date: date = record["transaction_date"]
        if transaction_date is None:
            raise TORCValidationError("Resumo de vendas sem data de RV")

        canonical: MutableMapping[str, object] = {
            "nsu": str(record["nsu"]),
            "authorization_code": record.get("authorization_code"),
            "amount": str(gross_amount.quantize(Decimal("0.01"))),
            "transaction_date": transaction_date,
            "card_brand": record.get("card_brand"),
            "card_last_4": record.get("card_last_4"),
            "mdr_rate": str(mdr_rate) if mdr_rate is not None else None,
            "mdr_amount": str(discount_amount.quantize(Decimal("0.01"))),
            "net_amount": str(net_amount.quantize(Decimal("0.01"))),
            "status": "approved",
        }

        return dict(canonical)

    def _parse_header(self, line: str) -> Dict[str, object]:
        fields = self._split(line, expected=10)
        return {
            "record_type": "00",
            "filiacao": fields[1],
            "data_emissao": self._parse_date(fields[2]),
            "data_movimento": self._parse_date(fields[3]),
            "descricao": fields[4],
            "adquirente": fields[5],
            "nome_comercial": fields[6],
            "sequencia": fields[7],
            "processamento": fields[8],
            "versao": fields[9],
        }

    def _parse_resumo_vendas(self, line: str) -> Dict[str, object]:
        fields = self._split(line, expected=14)
        gross_amount = self._parse_decimal(fields[6])
        discount_amount = self._parse_decimal(fields[7])
        net_amount = self._parse_decimal(fields[8])
        settlement_date = self._parse_date(fields[2])
        transaction_date = self._parse_date(fields[3])
        brand_code = fields[13] if len(fields) > 13 else ""
        brand = self._map_brand(brand_code)

        return {
            "record_type": "01",
            "filiacao": fields[1],
            "settlement_date": settlement_date,
            "transaction_date": transaction_date,
            "nsu": fields[4],
            "cvs": int(fields[5]) if fields[5] else 0,
            "gross_amount": gross_amount,
            "discount_amount": discount_amount,
            "net_amount": net_amount,
            "summary_type": fields[9],
            "bank": fields[10] if len(fields) > 10 else None,
            "agency": fields[11] if len(fields) > 11 else None,
            "account": fields[12] if len(fields) > 12 else None,
            "card_brand": brand,
        }

    def _parse_detalhe_cv(self, line: str) -> Dict[str, object]:
        fields = self._split(line)
        nsu_rv = fields[2] if len(fields) > 2 else ""
        card_number = fields[7] if len(fields) > 7 else ""
        card_last_4 = card_number[-4:] if len(card_number) >= 4 else None

        compra = (
            self._parse_decimal(fields[16])
            if len(fields) > 16 and fields[16]
            else None
        )
        saque = (
            self._parse_decimal(fields[17])
            if len(fields) > 17 and fields[17]
            else None
        )

        return {
            "record_type": "05",
            "nsu_cv": fields[9] if len(fields) > 9 else "",
            "nsu_rv": nsu_rv,
            "cartao_last4": card_last_4,
            "autorizacao": fields[19] if len(fields) > 19 else None,
            "hora": fields[12] if len(fields) > 12 else None,
            "terminal": fields[13] if len(fields) > 13 else None,
            "tipo_captura": self._map_capture_type(fields[14])
            if len(fields) > 14
            else None,
            "codigo_servico": fields[20] if len(fields) > 20 else None,
            "compre_saque": {
                "valor_compra": compra,
                "valor_saque": saque,
            },
        }

    def _parse_total_arquivo(self, line: str) -> Dict[str, object]:
        fields = self._split(line)
        total = fields[-1] if fields else "0"
        return {
            "record_type": "04",
            "total_registros": total,
        }

    def _parse_date(self, value: str) -> Optional[date]:
        if not value or value == "00000000":
            return None
        try:
            parsed = datetime.strptime(value, "%d%m%Y")
        except ValueError as exc:
            raise TORCValidationError(f"Data inválida: {value}") from exc
        return parsed.date()

    def _parse_decimal(self, value: str) -> Decimal:
        if not value:
            return Decimal("0")
        try:
            return (Decimal(value) / Decimal("100")).quantize(Decimal("0.01"))
        except Exception as exc:
            raise TORCValidationError(f"Valor monetário inválido: {value}") from exc

    def _map_capture_type(self, code: str) -> str:
        mapping = {
            "1": "manual",
            "2": "pos",
            "3": "pdv",
            "4": "to",
            "5": "internet",
            "6": "leitor_trilha",
        }
        return mapping.get(code, "unknown")

    def _map_brand(self, code: str) -> Optional[str]:
        if not code:
            return None
        return self.BRAND_MAPPING.get(code.upper(), "other")

    def _split(self, line: str, expected: Optional[int] = None) -> List[str]:
        fields = [field.strip() for field in line.split(",")]
        if expected is not None and len(fields) < expected:
            fields.extend([""] * (expected - len(fields)))
        return fields


__all__ = ["RedeTORCParser", "TORCValidationError", "ValidationError"]

