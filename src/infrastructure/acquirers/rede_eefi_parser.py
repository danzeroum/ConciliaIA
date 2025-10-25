"""Parser for Rede EEFI (Extrato Eletrônico Financeiro) files."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, List, Optional

from pydantic import BaseModel, Field, ValidationError, field_validator

from src.domain.entities import TransactionStatus
from src.domain.value_objects import Acquirer

from .base_parser import BaseAcquirerParser


def _slice(text: str, start: int, end: int) -> str:
    """Safely slice a string returning an empty string when the range is invalid."""

    if start >= len(text):
        return ""
    return text[start:end]


def _parse_decimal(value: str) -> Decimal:
    """Parse Rede numeric fields (999999999999999) into Decimal with 2 places."""

    stripped = value.strip()
    if not stripped:
        return Decimal("0.00")

    sign = 1
    if stripped.startswith("-"):
        sign = -1
        stripped = stripped[1:]
    elif stripped.endswith("-"):
        sign = -1
        stripped = stripped[:-1]

    digits = "".join(ch for ch in stripped if ch.isdigit())
    if not digits:
        return Decimal("0.00")

    quant = Decimal(sign) * Decimal(digits)
    result = quant / Decimal(100)
    return result.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _parse_date(value: str) -> Optional[date]:
    stripped = value.strip()
    if not stripped:
        return None
    for fmt in ("%d%m%Y", "%Y%m%d"):
        try:
            return datetime.strptime(stripped, fmt).date()
        except ValueError:
            continue
    return None


BANDEIRAS: Dict[str, str] = {
    "0": "OUTRAS",
    "1": "MASTERCARD",
    "2": "DINERS",
    "3": "VISA",
    "4": "CABAL",
    "5": "HIPERCARD",
    "6": "SOROCRED",
    "7": "CUP",
    "8": "CRED-SYSTEM",
    "9": "SICREDI",
    "A": "AVISTA",
    "B": "BANESCARD",
    "E": "ELO",
    "J": "JCB",
    "X": "AMEX",
    "Z": "CREDZ",
}


STATUS_MAP: Dict[str, TransactionStatus] = {
    "00": TransactionStatus.APPROVED,
    "08": TransactionStatus.APPROVED,
    "09": TransactionStatus.CANCELLED,
    "11": TransactionStatus.CANCELLED,
    "12": TransactionStatus.CANCELLED,
    "13": TransactionStatus.CANCELLED,
    "17": TransactionStatus.CANCELLED,
}


TIPOS_TRANSACAO: Dict[str, str] = {
    "01": "avista",
    "02": "parcelado_sem_juros",
    "03": "parcelado_iata",
    "04": "rotativo_dolar",
    "05": "cdc",
    "06": "pre_datada",
    "07": "trishop",
    "08": "construcard",
    "17": "negociacao_desfeita",
}


CHARGEBACK_CODES = {"16", "18", "23"}


class Registro030Header(BaseModel):
    """Registro 030 – header do arquivo."""

    tipo_registro: str = Field(pattern=r"^030$")
    data_emissao: date
    identificacao: str
    descricao: str
    nome_comercial: str
    sequencia_movimento: int
    numero_pv_grupo: str
    tipo_processamento: str
    versao_arquivo: str

    @classmethod
    def from_line(cls, line: str) -> "Registro030Header":
        data = {
            "tipo_registro": _slice(line, 0, 3),
            "data_emissao": _parse_date(_slice(line, 3, 11)),
            "identificacao": _slice(line, 11, 19).strip(),
            "descricao": _slice(line, 19, 53).strip(),
            "nome_comercial": _slice(line, 53, 75).strip(),
            "sequencia_movimento": int(_slice(line, 75, 81) or "0"),
            "numero_pv_grupo": _slice(line, 81, 90).strip(),
            "tipo_processamento": _slice(line, 90, 105).strip(),
            "versao_arquivo": _slice(line, 105, 125).strip(),
        }
        return cls.model_validate(data)

    @field_validator("data_emissao", mode="before")
    @classmethod
    def _validate_date(cls, value: date | str | None) -> date:
        if isinstance(value, date):
            return value
        parsed = _parse_date(value or "")
        if not parsed:
            raise ValueError("data_emissao inválida")
        return parsed


class Registro034Credito(BaseModel):
    """Registro 034 – ordens de crédito."""

    tipo_registro: str = Field(pattern=r"^034$")
    numero_pv: str
    numero_documento: str
    data_lancamento: date
    valor_lancamento: Decimal
    indicador_credito: str
    banco: str
    agencia: str
    conta_corrente: str
    data_movimento: date
    numero_rv: str
    data_rv: date
    bandeira: str
    tipo_transacao: str
    valor_bruto_rv: Decimal
    valor_taxa_desconto: Decimal
    numero_parcela: str
    status_credito: str
    numero_pv_original: str

    @classmethod
    def from_line(cls, line: str) -> "Registro034Credito":
        data = {
            "tipo_registro": _slice(line, 0, 3),
            "numero_pv": _slice(line, 3, 12).strip(),
            "numero_documento": _slice(line, 12, 23).strip(),
            "data_lancamento": _parse_date(_slice(line, 23, 31)),
            "valor_lancamento": _parse_decimal(_slice(line, 31, 46)),
            "indicador_credito": _slice(line, 46, 47).strip(),
            "banco": _slice(line, 47, 50).strip(),
            "agencia": _slice(line, 50, 56).strip(),
            "conta_corrente": _slice(line, 56, 67).strip(),
            "data_movimento": _parse_date(_slice(line, 67, 75)),
            "numero_rv": _slice(line, 75, 84).strip(),
            "data_rv": _parse_date(_slice(line, 84, 92)),
            "bandeira": _slice(line, 92, 93).strip() or "0",
            "tipo_transacao": _slice(line, 93, 94).strip() or "01",
            "valor_bruto_rv": _parse_decimal(_slice(line, 94, 109)),
            "valor_taxa_desconto": _parse_decimal(_slice(line, 109, 124)),
            "numero_parcela": _slice(line, 124, 129).strip(),
            "status_credito": _slice(line, 129, 131).strip() or "00",
            "numero_pv_original": _slice(line, 131, 140).strip() or _slice(line, 3, 12).strip(),
        }
        return cls.model_validate(data)

    @field_validator("data_lancamento", "data_movimento", "data_rv", mode="before")
    @classmethod
    def _validate_dates(cls, value: date | str | None) -> date:
        if isinstance(value, date):
            return value
        parsed = _parse_date(value or "")
        if not parsed:
            raise ValueError("data inválida")
        return parsed

    @field_validator("bandeira")
    @classmethod
    def _validate_bandeira(cls, value: str) -> str:
        if value and value in BANDEIRAS:
            return value
        raise ValueError(f"Bandeira inválida: {value}")

    @field_validator("tipo_transacao")
    @classmethod
    def _validate_tipo(cls, value: str) -> str:
        normalized = value.zfill(2)
        if normalized in TIPOS_TRANSACAO:
            return normalized
        raise ValueError(f"Tipo transação inválido: {value}")


class Registro038AjusteDebito(BaseModel):
    """Registro 038 – ajustes a débito (chargebacks)."""

    tipo_registro: str = Field(pattern=r"^038$")
    numero_pv: str
    numero_documento: str
    data_emissao: date
    valor_debito: Decimal
    indicador_debito: str
    banco: str
    agencia: str
    conta_corrente: str
    numero_rv_original: str
    data_rv_original: date
    valor_credito_original: Decimal
    motivo_debito_codigo: str
    motivo_debito_descricao: str
    tipo_debito: str
    valor_debito_total: Decimal
    valor_pendente: Decimal

    @classmethod
    def from_line(cls, line: str) -> "Registro038AjusteDebito":
        data = {
            "tipo_registro": _slice(line, 0, 3),
            "numero_pv": _slice(line, 3, 12).strip(),
            "numero_documento": _slice(line, 12, 23).strip(),
            "data_emissao": _parse_date(_slice(line, 23, 31)),
            "valor_debito": _parse_decimal(_slice(line, 31, 46)),
            "indicador_debito": _slice(line, 46, 47).strip(),
            "banco": _slice(line, 47, 50).strip(),
            "agencia": _slice(line, 50, 56).strip(),
            "conta_corrente": _slice(line, 56, 67).strip(),
            "numero_rv_original": _slice(line, 67, 76).strip(),
            "data_rv_original": _parse_date(_slice(line, 76, 84)),
            "valor_credito_original": _parse_decimal(_slice(line, 84, 99)),
            "motivo_debito_codigo": _slice(line, 99, 103).strip(),
            "motivo_debito_descricao": _slice(line, 103, 131).strip(),
            "tipo_debito": _slice(line, 271, 272).strip() or "T",
            "valor_debito_total": _parse_decimal(_slice(line, 272, 287)),
            "valor_pendente": _parse_decimal(_slice(line, 287, 302)),
        }
        return cls.model_validate(data)

    @field_validator("data_emissao", "data_rv_original", mode="before")
    @classmethod
    def _validate_dates(cls, value: date | str | None) -> date:
        if isinstance(value, date):
            return value
        parsed = _parse_date(value or "")
        if not parsed:
            raise ValueError("data inválida")
        return parsed


@dataclass
class _ParsedRecord:
    record_type: str
    payload: Dict[str, object]


class RedeEEFIParser(BaseAcquirerParser):
    """Parser especializado para arquivos EEFI da Rede."""

    def __init__(self) -> None:
        super().__init__(Acquirer.REDE)
        self._errors: List[Dict[str, object]] = []

    def _parse_raw_data(self, raw_data: str | bytes | Dict | List[Dict]) -> List[Dict]:
        self._errors.clear()

        if isinstance(raw_data, list):
            return raw_data
        if isinstance(raw_data, dict):
            return [raw_data]

        if isinstance(raw_data, bytes):
            content = raw_data.decode("latin-1", errors="ignore")
        else:
            content = str(raw_data)

        lines = [line.rstrip("\r\n") for line in content.splitlines() if line.strip()]
        parsed: List[_ParsedRecord] = []

        for line_number, line in enumerate(lines, start=1):
            record_type = line[:3]
            try:
                if record_type == "030":
                    header = Registro030Header.from_line(line)
                    parsed.append(_ParsedRecord(record_type="030", payload=header.model_dump()))
                elif record_type == "034":
                    record = Registro034Credito.from_line(line)
                    payload = record.model_dump()
                    payload["record_type"] = "034"
                    parsed.append(_ParsedRecord(record_type="034", payload=payload))
                elif record_type == "038":
                    record = Registro038AjusteDebito.from_line(line)
                    payload = record.model_dump()
                    payload["record_type"] = "038"
                    parsed.append(_ParsedRecord(record_type="038", payload=payload))
            except ValidationError as exc:
                self.logger.warning(
                    "rede_eefi_record_invalid",
                    line_number=line_number,
                    record_type=record_type,
                    error=str(exc),
                )
                self._errors.append(
                    {
                        "line": line_number,
                        "record_type": record_type,
                        "error": exc.errors(),
                    }
                )

        return [record.payload for record in parsed]

    def _validate_data(self, records: List[Dict]) -> List[Dict]:
        valid: List[Dict] = []
        for record in records:
            record_type = record.get("record_type")
            if record_type == "034":
                if record.get("numero_rv") and record.get("valor_bruto_rv"):
                    valid.append(record)
            elif record_type == "038":
                if record.get("motivo_debito_codigo") and record.get("valor_debito_total"):
                    valid.append(record)
        return valid

    def _normalize_to_canonical(self, record: Dict) -> Dict:
        record_type = record.get("record_type")
        if record_type == "038":
            return self._normalize_debit(record)
        return self._normalize_credit(record)

    def _normalize_credit(self, record: Dict) -> Dict:
        gross: Decimal = record["valor_bruto_rv"]
        net: Decimal = record.get("valor_lancamento") or gross
        fee: Decimal = record.get("valor_taxa_desconto") or Decimal("0.00")

        if net <= Decimal("0.00"):
            net = gross - fee if fee else gross
        if fee == Decimal("0.00") and gross > net:
            fee = (gross - net).quantize(Decimal("0.01"))
        if gross <= net and fee > Decimal("0.00"):
            gross = (net + fee).quantize(Decimal("0.01"))

        transaction_date: date = record["data_movimento"]
        status = STATUS_MAP.get(record.get("status_credito"), TransactionStatus.APPROVED)

        auth_code = (record.get("numero_documento") or "").strip()
        if auth_code and len(auth_code) > 10:
            auth_code = auth_code[:10]

        canonical: Dict[str, object] = {
            "nsu": record.get("numero_rv") or auth_code or record.get("numero_documento"),
            "authorization_code": auth_code or None,
            "amount": f"{gross.quantize(Decimal('0.01'))}",
            "transaction_date": transaction_date,
            "card_brand": BANDEIRAS.get(record.get("bandeira", ""), "unknown"),
            "card_last_4": None,
            "mdr_amount": f"{fee.quantize(Decimal('0.01'))}" if fee else None,
            "net_amount": f"{net.quantize(Decimal('0.01'))}" if net else None,
            "mdr_rate": None,
            "status": status.value,
        }
        return canonical

    def _normalize_debit(self, record: Dict) -> Dict:
        amount: Decimal = record.get("valor_debito_total") or record.get("valor_debito")
        transaction_date: date = record.get("data_emissao")

        status = TransactionStatus.CHARGEBACK.value
        if record.get("motivo_debito_codigo") not in CHARGEBACK_CODES:
            status = TransactionStatus.CANCELLED.value

        auth_code = (record.get("numero_documento") or "").strip()
        if auth_code and len(auth_code) > 10:
            auth_code = auth_code[:10]

        canonical: Dict[str, object] = {
            "nsu": record.get("numero_rv_original") or auth_code or record.get("numero_documento"),
            "authorization_code": auth_code or None,
            "amount": f"{amount.quantize(Decimal('0.01'))}",
            "transaction_date": transaction_date,
            "card_brand": None,
            "card_last_4": None,
            "mdr_amount": None,
            "net_amount": None,
            "mdr_rate": None,
            "status": status,
        }
        return canonical

    @property
    def errors(self) -> List[Dict[str, object]]:
        return list(self._errors)


__all__ = ["RedeEEFIParser"]

