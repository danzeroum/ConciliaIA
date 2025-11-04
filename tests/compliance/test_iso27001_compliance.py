#!/usr/bin/env python3
"""Testes de conformidade ISO 27001 (Sincronizado com Platinum v2)"""

import subprocess
import json
import pytest
import os
from pathlib import Path

# Define a raiz do projeto (sobe 3 níveis de tests/compliance/test_iso27001_compliance.py)
PROJECT_ROOT = Path(__file__).parent.parent.parent.resolve()

# Conteúdo mínimo válido para o ledger
VALID_LEDGER_ENTRY = '{"timestamp": "2025-12-01T10:00:00Z", "task": "test", "status": "success", "btv_spec": "test"}\n'


def get_script_path(script_relative_path):
    """Retorna caminho absoluto para scripts"""
    return PROJECT_ROOT / script_relative_path


def test_risk_assessment_workflow(tmp_path, monkeypatch):
    """Verifica fluxo completo de avaliação de riscos"""
    monkeypatch.chdir(tmp_path)

    script_path = get_script_path("scripts/compliance/frameworks/iso27001/risk-assessment.py")

    # Adicionar risco
    result = subprocess.run(
        ["python3", str(script_path),
         "add",
         "--id", "RISK-001",
         "--title", "Unauthorized Access",
         "--description", "Risk of unauthorized access to ledger",
         "--asset", "ledger.jsonl",
         "--threat", "Malicious insider",
         "--vulnerability", "Weak access controls",
         "--likelihood", "3",
         "--impact", "4",
         "--controls", "file_permissions", "audit_logging",
         "--owner", "security@example.com"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=True
    )

    assert "Risco adicionado" in result.stdout

    # Definir tratamento
    result = subprocess.run(
        ["python3", str(script_path),
         "treat", "RISK-001",
         "--type", "mitigate",
         "--plan", "Implement MFA and enhanced monitoring",
         "--residual-likelihood", "1",
         "--residual-impact", "2"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=True
    )

    assert "Tratamento definido" in result.stdout

    register_file = tmp_path / ".buildtovalue/compliance/reports/iso27001-risk-register.json"
    assert register_file.exists()

    with open(register_file) as f:
        register = json.load(f)
        assert len(register["risks"]) == 1
        assert register["risks"][0]["risk_id"] == "RISK-001"
        assert register["risks"][0]["status"] == "treated"


def test_risk_matrix_export(tmp_path, monkeypatch):
    """Verifica exportação de matriz de riscos"""
    monkeypatch.chdir(tmp_path)

    register_file = tmp_path / ".buildtovalue/compliance/reports/iso27001-risk-register.json"
    register_file.parent.mkdir(parents=True, exist_ok=True)

    # Registro de risco simulado (deve corresponder à estrutura do script Platinum)
    register = {
        "btv_spec": "ESPEC-COMPLIANCE-FRAMEWORKS-PLATINUM",
        "framework": "ISO-27001",
        "risks": [
            {
                "risk_id": "R1", "title": "R1 Title", "owner": "Owner1",
                "inherent_risk": {"likelihood": 3, "impact": 4, "score": 12, "level": "HIGH"}
            },
            {
                "risk_id": "R2", "title": "R2 Title", "owner": "Owner2",
                "inherent_risk": {"likelihood": 2, "impact": 2, "score": 4, "level": "LOW"}
            }
        ],
        "last_assessment": "2025-12-01T00:00:00Z"
    }

    with open(register_file, 'w') as f:
        json.dump(register, f)

    script_path = get_script_path("scripts/compliance/frameworks/iso27001/risk-assessment.py")

    output_file = tmp_path / "risk-matrix.md"

    result = subprocess.run(
        ["python3", str(script_path),
         "export-matrix",
         "--output", str(output_file)],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=True
    )

    assert output_file.exists()
    content = output_file.read_text()
    assert "Risk Matrix" in content
    assert "CRITICAL" in content


def test_isms_audit(tmp_path, monkeypatch):
    """Verifica auditoria ISMS"""
    monkeypatch.chdir(tmp_path)

    # Correção (RCA-2): Criar todas as dependências que o script 'isms-audit.sh' verifica
    (tmp_path / ".buildtovalue/archives").mkdir(parents=True, exist_ok=True)
    (tmp_path / ".buildtovalue/policies").mkdir(parents=True, exist_ok=True)
    (tmp_path / ".buildtovalue/compliance").mkdir(parents=True, exist_ok=True)

    (tmp_path / ".buildtovalue/ledger.jsonl").write_text(VALID_LEDGER_ENTRY)
    (tmp_path / ".buildtovalue/archives/test.gz").touch()
    (tmp_path / ".buildtovalue/policies/security-policy.yaml").touch()  # Dependência A.5.1
    (tmp_path / ".buildtovalue/compliance/change-control-log.jsonl").touch()  # Dependência A.9.4
    (tmp_path / ".buildtovalue/compliance/breach-log.jsonl").touch()  # Dependência A.16.1

    script_path = get_script_path("scripts/compliance/frameworks/iso27001/isms-audit.sh")

    result = subprocess.run(
        ["bash", str(script_path), "report"],
        cwd=tmp_path,
        capture_output=True,
        text=True
    )

    assert result.returncode == 0, f"Script falhou: {result.stderr}"

    report_files = list((tmp_path / ".buildtovalue/compliance/reports").glob("iso27001-isms-audit-*.json"))
    assert len(report_files) > 0, "O script de auditoria ISMS não gerou um relatório .json"

    with open(report_files[0]) as f:
        report = json.load(f)
        assert report["framework"] == "ISO-27001"
        assert "compliance_rate_percent" in report["summary"]
        assert report["summary"]["compliance_rate_percent"] > 50  # Deve ter >50% com este setup


def test_certification_readiness(tmp_path, monkeypatch):
    """Verifica avaliação de prontidão para certificação"""
    monkeypatch.chdir(tmp_path)

    # Correção (RCA-2): Criar todas as dependências
    (tmp_path / ".buildtovalue/policies").mkdir(parents=True, exist_ok=True)
    (tmp_path / ".buildtovalue/compliance").mkdir(parents=True, exist_ok=True)
    (tmp_path / ".buildtovalue/archives").mkdir(parents=True, exist_ok=True)  # Adicionado para A.12.3

    (tmp_path / ".buildtovalue/ledger.jsonl").write_text(VALID_LEDGER_ENTRY)
    (tmp_path / ".buildtovalue/compliance/breach-log.jsonl").touch()
    (tmp_path / ".buildtovalue/policies/security-policy.yaml").touch()
    (tmp_path / ".buildtovalue/compliance/change-control-log.jsonl").touch()  # Adicionado para A.9.4
    (tmp_path / ".buildtovalue/archives/test.gz").touch()  # Adicionado para A.12.3

    script_path = get_script_path("scripts/compliance/frameworks/iso27001/isms-audit.sh")

    result = subprocess.run(
        ["bash", str(script_path), "report"],
        cwd=tmp_path,
        capture_output=True,
        text=True
    )

    assert result.returncode == 0, f"Script falhou: {result.stderr}"

    report_files = list((tmp_path / ".buildtovalue/compliance/reports").glob("iso27001-isms-audit-*.json"))
    assert len(report_files) > 0, "O script de auditoria ISMS não gerou um relatório .json"

    with open(report_files[0]) as f:
        report = json.load(f)
        assert "certification_readiness" in report["summary"]
