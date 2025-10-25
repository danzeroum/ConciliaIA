"""Validate Rede EDI files and print basic statistics."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable

from src.infrastructure.acquirers import RedeEDIParser


def load_file(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(path)
    return path.read_text(encoding="latin-1")


def summarize(file_type: str, content: str) -> None:
    parser = RedeEDIParser()
    transactions = parser.parse(content, tenant_id="validation")
    print(f"{file_type}: {len(transactions)} transações válidas")
    if transactions:
        first = transactions[0]
        print(
            "  Primeiro registro:",
            first.nsu.value,
            first.transaction_date.isoformat(),
            first.amount.amount,
        )


def main(argv: Iterable[str] | None = None) -> None:
    argument_parser = argparse.ArgumentParser(description="Validate Rede EDI files")
    argument_parser.add_argument("--eevc", type=Path, help="Arquivo EEVC (Vendas Crédito)")
    argument_parser.add_argument("--eevd", type=Path, help="Arquivo EEVD (Vendas Débito)")
    argument_parser.add_argument("--eefi", type=Path, help="Arquivo EEFI (Financeiro)")
    argument_parser.add_argument("--eesa", type=Path, help="Arquivo EESA (Saldos em Aberto)")
    args = argument_parser.parse_args(argv)

    if not any((args.eevc, args.eevd, args.eefi, args.eesa)):
        argument_parser.error("Informe pelo menos um arquivo para validar")

    if args.eevc:
        summarize("EEVC", load_file(args.eevc))
    if args.eevd:
        summarize("EEVD", load_file(args.eevd))
    if args.eefi:
        summarize("EEFI", load_file(args.eefi))
    if args.eesa:
        summarize("EESA", load_file(args.eesa))


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    main()
