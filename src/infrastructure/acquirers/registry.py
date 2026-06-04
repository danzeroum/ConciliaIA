"""Pluggable registry of acquirer parsers.

Single place that maps a payment :class:`Acquirer` to the parser formats it
supports. The ``/api/v1/acquirers`` endpoint reads from here so the frontend is
no longer coupled to a hardcoded enum, and onboarding a new acquirer/format is a
one-line change (register the parser class) rather than edits scattered across
the UI and the API.
"""

from __future__ import annotations

from typing import Dict, List, Optional, Type

from src.domain.value_objects import Acquirer

from .base_parser import BaseAcquirerParser
from .cielo_agiliza_parser import CieloAgilizaParser
from .cielo_edi_parser import CieloEDIParser
from .rede_edi_parser import RedeEDIParser
from .rede_eefi_parser import RedeEEFIParser
from .rede_torc_parser import RedeTORCParser
from .stone_parser import StoneParser

# acquirer -> {format_id: parser_class}
ACQUIRER_PARSERS: Dict[Acquirer, Dict[str, Type[BaseAcquirerParser]]] = {
    Acquirer.CIELO: {"agiliza": CieloAgilizaParser, "edi": CieloEDIParser},
    Acquirer.REDE: {
        "edi": RedeEDIParser,
        "eefi": RedeEEFIParser,
        "torc": RedeTORCParser,
    },
    Acquirer.STONE: {"api": StoneParser},
}

# Human-friendly labels for every known acquirer (including those without a
# parser yet, so the UI can show them as "coming soon").
ACQUIRER_LABELS: Dict[Acquirer, str] = {
    Acquirer.CIELO: "Cielo",
    Acquirer.REDE: "Rede",
    Acquirer.STONE: "Stone",
    Acquirer.MERCADO_PAGO: "Mercado Pago",
    Acquirer.GETNET: "GetNet",
    Acquirer.PAGSEGURO: "PagSeguro",
}


def list_acquirers() -> List[dict]:
    """Return metadata for every acquirer, including parser availability."""
    acquirers: List[dict] = []
    for acquirer in Acquirer:
        parsers = ACQUIRER_PARSERS.get(acquirer, {})
        acquirers.append(
            {
                "id": acquirer.value,
                "label": ACQUIRER_LABELS.get(acquirer, acquirer.value.title()),
                "parser_formats": sorted(parsers.keys()),
                "supported": bool(parsers),
            }
        )
    return acquirers


def get_parser_class(
    acquirer: Acquirer | str, fmt: str
) -> Optional[Type[BaseAcquirerParser]]:
    """Return the parser class registered for ``acquirer``/``fmt`` (or None)."""
    if isinstance(acquirer, str):
        try:
            acquirer = Acquirer(acquirer)
        except ValueError:
            return None
    return ACQUIRER_PARSERS.get(acquirer, {}).get(fmt)


__all__ = [
    "ACQUIRER_PARSERS",
    "ACQUIRER_LABELS",
    "list_acquirers",
    "get_parser_class",
]
