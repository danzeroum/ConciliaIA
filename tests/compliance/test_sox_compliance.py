#!/usr/bin/env python3
"""Testes de conformidade SOX (Sincronizado com Platinum)"""

import subprocess
import json
import pytest
import os
from pathlib import Path

# Define a raiz do projeto (sobe 3 níveis de tests/compliance/test_sox_compliance.py)
PROJECT_ROOT = Path(__file__).parent.parent.parent.resolve()

# Conteúdo mínimo válido para o ledger
VALID_LEDGER_ENTRY = '{"timestamp": "2025-12-01T10:00:00Z", "task": "test", "status": "success", "btv_spec": "test"}\n'


def get_script_path(script_relative_path):
    """Retorna caminho absoluto para scripts"""
    return PROJECT_ROOT / script_relative_path


def test_audit_trail_integrity(tmp_path, monkeypatch):
    """Verifica validação de integridade do audit trail"""
    monkeypatch.chdir(tmp_path)

    ledger = tmp_path / ".buildtovalue/ledger.jsonl"
    ledger.parent.mkdir(parents=True, exist_ok=True)

    # Criar ledger válido
    entries = [
        {"timestamp": "2025-12-01T10:00:00Z", "task": "task1", "status": "success", "btv_spec": "test"},
        {"timestamp": "2025-12-01T11:00:00Z", "task": "task2", "status": "success", "btv_spec": "test"},
    ]

    with open(ledger, 'w') as f:
        for entry in entries:
            f.write(json.dumps(entry) + "\n")

    script_path = get_script_path("scripts/compliance/frameworks/sox/audit-trail-validator.sh")

    result = subprocess.run(
        ["bash", str(script_path), "integrity"],
        cwd=tmp_path,
        capture_output=True,
        text=True
    )

    assert result.returncode == 0, f"Script falhou: {result.stderr}"
    assert "Audit trail válido" in result.stdout


def test_immutability_check(tmp_path, monkeypatch):
    """Verifica detecção de tampering"""
    monkeypatch.chdir(tmp_path)

    archives_dir = tmp_path / ".buildtovalue/archives"
    archives_dir.mkdir(parents=True, exist_ok=True)

    archive = archives_dir / "ledger-20251201.jsonl.gz"
    archive.write_text("test data")

    checksum = subprocess.run(
        ["sha256sum", str(archive)],
        capture_output=True,
        text=True,
        check=True
    )

    checksum_file = archives_dir / "ledger-20251201.jsonl.gz.sha256"
    checksum_file.write_text(checksum.stdout.split()[0])

    script_path = get_script_path("scripts/compliance/frameworks/sox/audit-trail-validator.sh")

    result = subprocess.run(
        ["bash", str(script_path), "immutability"],
        cwd=tmp_path,
        capture_output=True,
        text=True
    )

    assert result.returncode == 0, f"Script falhou: {result.stderr}"
    assert "Nenhuma alteração não autorizada" in result.stdout


def test_change_control_workflow(tmp_path, monkeypatch):
    """Verifica fluxo de controle de mudanças"""
    monkeypatch.chdir(tmp_path)

    script_path = get_script_path("scripts/compliance/frameworks/sox/change-control.py")

    # 1. Registrar mudança
    result_record = subprocess.run(
        ["python3", str(script_path),
         "record", "security_patch",
         "Apply security update",
         "--requester", "dev@example.com",
         "--approver", "manager@example.com",
         "--risk", "medium"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=True
    )

    # Extrair change_id do stdout do script
    change_id = None
    try:
        # O script Platinum imprime um JSON no stdout
        record_json = json.loads(result_record.stdout.splitlines()[-1])
        change_id = record_json.get("change_id")
    except json.JSONDecodeError:
        pass

    assert change_id is not None, f"Não foi possível extrair change_id do stdout: {result_record.stdout}"

    # Verificar se o log foi criado
    log_file = tmp_path / ".buildtovalue/compliance/change-control-log.jsonl"
    assert log_file.exists(), "O script change-control.py não criou o arquivo de log."

    # 2. Aprovar mudança
    result_approve = subprocess.run(
        ["python3", str(script_path),
         "approve", change_id,
         "--actor", "manager@example.com"],  # Argumento --actor obrigatório
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=True
    )

    assert "Mudança aprovada" in result_approve.stdout

    # Verificar se o log foi atualizado
    with open(log_file, 'r') as f:
        lines = f.readlines()
        assert len(lines) == 1  # O script deve atualizar a linha
        final_change = json.loads(lines[0])
        assert final_change["change_id"] == change_id
        assert final_change["status"] == "approved"


def test_sox_report_generation(tmp_path, monkeypatch):
    """Verifica geração de relatório SOX"""
    monkeypatch.chdir(tmp_path)

    ledger = tmp_path / ".buildtovalue/ledger.jsonl"
    ledger.parent.mkdir(parents=True, exist_ok=True)
    ledger.write_text(VALID_LEDGER_ENTRY)

    script_path = get_script_path("scripts/compliance/frameworks/sox/audit-trail-validator.sh")

    result = subprocess.run(
        ["bash", str(script_path), "report"],
        cwd=tmp_path,
        capture_output=True,
        text=True
    )

    assert result.returncode == 0, f"Script falhou: {result.stderr}"

    report_files = list((tmp_path / ".buildtovalue/compliance/reports").glob("sox-audit-trail-*.json"))
    assert len(report_files) > 0, "O script de relatório não criou nenhum arquivo .json"

    # Validar que o JSON não está vazio
    with open(report_files[0]) as f:
        try:
            report = json.load(f)
        except json.JSONDecodeError:
            pytest.fail(f"Relatório SOX gerado não é JSON válido ou está vazio. Conteúdo: {f.read()}")

    assert "framework" in report
    assert report["framework"] == "SOX (Sarbanes-Oxley Act)"
