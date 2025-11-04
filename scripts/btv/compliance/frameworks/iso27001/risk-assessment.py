#!/usr/bin/env python3
"""
BuildToValue v7.4-Platinum - ISO 27001 Risk Assessment
Gerencia o registro de riscos (Risk Register)
Em conformidade com ESPEC-COMPLIANCE-FRAMEWORKS-PLATINUM
"""

import sys
import json
import argparse
from datetime import datetime, UTC
from pathlib import Path

# --- Configuração ---
REGISTER_FILE = Path(".buildtovalue/compliance/reports/iso27001-risk-register.json")
TIMESTAMP = datetime.now(UTC).isoformat().replace("+00:00", "Z")

RISK_MATRIX = {
    (1, 1): 1, (1, 2): 2, (1, 3): 3, (1, 4): 4, (1, 5): 5,
    (2, 1): 2, (2, 2): 4, (2, 3): 6, (2, 4): 8, (2, 5): 10,
    (3, 1): 3, (3, 2): 6, (3, 3): 9, (3, 4): 12, (3, 5): 15,
    (4, 1): 4, (4, 2): 8, (4, 3): 12, (4, 4): 16, (4, 5): 20,
    (5, 1): 5, (5, 2): 10, (5, 3): 15, (5, 4): 20, (5, 5): 25,
}


def log(msg: str):
    print(f"🧩 [ISO 27001]: {msg}")


def get_risk_level(score: int) -> str:
    if score <= 5: return "LOW"
    if score <= 12: return "MEDIUM"
    if score <= 20: return "HIGH"
    return "CRITICAL"


def load_register() -> dict:
    REGISTER_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not REGISTER_FILE.exists():
        return {
            "btv_spec": "ESPEC-COMPLIANCE-FRAMEWORKS-PLATINUM",
            "framework": "ISO-27001",
            "document_type": "Risk-Register",
            "last_updated": TIMESTAMP,
            "risks": []
        }
    with open(REGISTER_FILE, "r") as f:
        return json.load(f)


def save_register(register: dict):
    REGISTER_FILE.parent.mkdir(parents=True, exist_ok=True)
    register["last_updated"] = TIMESTAMP
    with open(REGISTER_FILE, "w") as f:
        json.dump(register, f, indent=2)


# --- Subcomandos ---------------------------------------------------------------
def add_risk(args):
    register = load_register()
    score = RISK_MATRIX.get((args.likelihood, args.impact), 0)
    level = get_risk_level(score)

    risk = {
        "risk_id": args.id,
        "title": args.title,
        "description": args.description,
        "asset": args.asset,
        "threat": args.threat,
        "vulnerability": args.vulnerability,
        "owner": args.owner,
        "status": "identified",
        "created_at": TIMESTAMP,
        "inherent_risk": {
            "likelihood": args.likelihood,
            "impact": args.impact,
            "score": score,
            "level": level
        },
        "existing_controls": args.controls,
        "treatment": None,
        "residual_risk": None
    }

    register["risks"].append(risk)
    save_register(register)
    log(f"Risco adicionado: {args.id} (Nível: {level})")
    print(f"Risco adicionado {args.id}")
    sys.exit(0)


def treat_risk(args):
    register = load_register()

    target = None
    for risk in register["risks"]:
        if risk["risk_id"] == args.risk_id:
            target = risk
            break

    if not target:
        log(f"Erro: Risco {args.risk_id} não encontrado.")
        sys.exit(1)

    residual_score = RISK_MATRIX.get((args.residual_likelihood, args.residual_impact), 0)
    residual_level = get_risk_level(residual_score)

    target["status"] = "treated"
    target["treatment"] = {
        "type": args.type,
        "plan": args.plan,
        "treated_at": TIMESTAMP
    }
    target["residual_risk"] = {
        "likelihood": args.residual_likelihood,
        "impact": args.residual_impact,
        "score": residual_score,
        "level": residual_level
    }

    save_register(register)
    log(f"Tratamento definido para: {args.risk_id} (Risco Residual: {residual_level})")
    print(f"Tratamento definido para {args.risk_id}")
    sys.exit(0)


def export_matrix(args):
    register = load_register()
    output_file = Path(args.output)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    matrix = [["-" for _ in range(5)] for _ in range(5)]

    for risk in register["risks"]:
        risk_data = risk.get("residual_risk") or risk.get("inherent_risk")
        if not risk_data:
            continue
        l = 4 - (risk_data["likelihood"] - 1)
        i = risk_data["impact"] - 1
        cell = matrix[l][i]
        matrix[l][i] = f"{cell}, {risk['risk_id']}" if cell != "-" else risk["risk_id"]

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(f"# ISO 27001 Risk Matrix (Generated: {TIMESTAMP})\n\n")
        f.write("`Likelihood ↓ | Impact →`\n")
        f.write("| 1 | 2 | 3 | 4 | 5 |\n")
        f.write("|:---:|:---:|:---:|:---:|:---:|\n")

        prob_labels = ["5 (High)", "4", "3", "2", "1 (Low)"]
        for r_idx, row in enumerate(matrix):
            f.write(f"| **{prob_labels[r_idx]}** | " + " | ".join(row) + " |\n")

        f.write("\n## Níveis de Risco\n")
        f.write("- **CRITICAL** (21-25)\n")
        f.write("- **HIGH** (13-20)\n")
        f.write("- **MEDIUM** (6-12)\n")
        f.write("- **LOW** (1-5)\n")

    log(f"Matriz de riscos exportada: {output_file}")
    print("🔍 [ISO Audit]: Iniciando Auditoria ISMS (ISO 27001)...")
    sys.exit(0)


# --- CLI ----------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="ISO 27001 Risk Assessment (BTV v7.4-Platinum)")
    sub = parser.add_subparsers(dest="command", required=True)

    # add
    p_add = sub.add_parser("add")
    p_add.add_argument("--id", required=True)
    p_add.add_argument("--title", required=True)
    p_add.add_argument("--description", required=True)
    p_add.add_argument("--asset", required=True)
    p_add.add_argument("--threat", required=True)
    p_add.add_argument("--vulnerability", required=True)
    p_add.add_argument("--owner", required=True)
    p_add.add_argument("--likelihood", type=int, choices=range(1, 6), required=True)
    p_add.add_argument("--impact", type=int, choices=range(1, 6), required=True)
    p_add.add_argument("--controls", nargs="+", default=[])
    p_add.set_defaults(func=add_risk)

    # treat
    p_treat = sub.add_parser("treat")
    p_treat.add_argument("risk_id")
    p_treat.add_argument("--type", required=True, choices=["mitigate", "accept", "transfer", "avoid"])
    p_treat.add_argument("--plan", required=True)
    p_treat.add_argument("--residual-likelihood", type=int, required=True, choices=range(1, 6))
    p_treat.add_argument("--residual-impact", type=int, required=True, choices=range(1, 6))
    p_treat.set_defaults(func=treat_risk)

    # export-matrix
    p_export = sub.add_parser("export-matrix")
    p_export.add_argument("--output", default="risk-matrix.md")
    p_export.set_defaults(func=export_matrix)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
