"""Enumeration of supported payment acquirers."""

from __future__ import annotations

from enum import Enum


class Acquirer(str, Enum):
    """Supported payment acquirers."""

    CIELO = "cielo"
    REDE = "rede"
    STONE = "stone"
    MERCADO_PAGO = "mercadopago"
    GETNET = "getnet"
    PAGSEGURO = "pagseguro"

    def __str__(self) -> str:  # pragma: no cover - trivial
        return self.value
