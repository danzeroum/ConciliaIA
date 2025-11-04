#!/usr/bin/env python3
"""
BuildToValue v7.4-Platinum - SOX Change Control
Registra e aprova mudanças em conformidade com SOX e
ESPEC-COMPLIANCE-FRAMEWORKS-PLATINUM.
"""

import sys
import json
import argparse
from datetime import datetime
from pathlib import Path

# --- Configuração ---
LOG_FILE = Path(".buildtovalue/compliance/change-control-log.jsonl")
TIMESTAMP = datetime.utcnow().isoformat() + "Z"


# --- Funções ---

def log(message: str):
    """Imprime uma mensagem de log formatada."""
    print(f"🔩 [SOX Change]: {message}")


def ensure_log_dir():
    """Garante que o diretório de log exista."""
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)


def find_change(change_id: str) -> (dict | None, list[dict]):
    """Encontra uma mudança específica no log."""
    if not LOG_FILE.exists():
        return None, []

    changes = []
    found_change = None
    with open(LOG_FILE, 'r') as f:
        for line in f:
            try:
                change = json.loads(line)
                if change.get("change_id") == change_id:
                    found_change = change
                else:
                    changes.append(change)
            except json.JSONDecodeError:
                continue
    return found_change, changes


def write_changes_to_log(changes: list[dict]):
    """Reescreve o arquivo de log com a lista de mudanças."""
    ensure_log_dir()
    with open(LOG_FILE, 'w') as f:
        for change in changes:
            f.write(json.dumps(change) + "\n")


# --- Comandos ---

def record_change(args: argparse.Namespace):
    """Registra uma nova solicitação de mudança (CHG)."""
    ensure_log_dir()

    change_id = f"CHG-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}"

    change_record = {
        "btv_spec": "ESPEC-COMPLIANCE-FRAMEWORKS-PLATINUM",
        "framework": "SOX",
        "change_id": change_id,
        "timestamp": TIMESTAMP,
        "type": args.type,
        "description": args.description,
        "requester": args.requester,
        "approver": args.approver,
        "risk_level": args.risk,
        "status": "pending_approval",
        "audit_trail": [
            {"timestamp": TIMESTAMP, "action": "created", "actor": args.requester}
        ]
    }

    with open(LOG_FILE, 'a') as f:
        f.write(json.dumps(change_record) + "\n")

    log(f"Mudança registrada: {change_id}")
    # Saída esperada pelo teste
    print(json.dumps({"status": "recorded", "change_id": change_id}))


def approve_change(args: argparse.Namespace):
    """Aprova uma mudança pendente."""
    change, other_changes = find_change(args.change_id)

    if not change:
        log(f"Erro: Mudança {args.change_id} não encontrada.")
        sys.exit(1)

    if change["status"] != "pending_approval":
        log(f"Erro: Mudança {args.change_id} não está pendente (status: {change['status']}).")
        sys.exit(1)

    change["status"] = "approved"
    change["approved_at"] = TIMESTAMP
    change["audit_trail"].append({
        "timestamp": TIMESTAMP,
        "action": "approved",
        "actor": args.actor
    })

    other_changes.append(change)
    write_changes_to_log(other_changes)

    log(f"Mudança aprovada: {args.change_id}")
    # Saída esperada pelo teste
    print(f"Mudança {args.change_id} aprovada.")


# --- Execução Principal ---
def main():
    parser = argparse.ArgumentParser(description="SOX Change Control (BTV v7.4-Platinum)")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Comando 'record'
    record_parser = subparsers.add_parser("record", help="Registrar uma nova mudança")
    record_parser.add_argument("type", help="Tipo de mudança (ex: schema, code, config)")
    record_parser.add_argument("description", help="Descrição da mudança")
    record_parser.add_argument("--requester", required=True, help="Email do solicitante")
    record_parser.add_argument("--approver", required=True, help="Email do aprovador")
    record_parser.add_argument("--risk", choices=["low", "medium", "high"], default="medium", help="Nível de risco")
    record_parser.set_defaults(func=record_change)

    # Comando 'approve'
    approve_parser = subparsers.add_parser("approve", help="Aprovar uma mudança")
    approve_parser.add_argument("change_id", help="ID da mudança (CHG-...)")
    approve_parser.add_argument("--actor", required=True, help="Email do aprovador que executa a ação")
    approve_parser.set_defaults(func=approve_change)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
