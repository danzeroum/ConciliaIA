#!/usr/bin/env python3
"""
Testes do scanner unificado de compliance
"""
import subprocess
import json
import pytest
from pathlib import Path


def test_unified_scan(tmp_path, monkeypatch):
    """Verifica scan unificado de todos os frameworks"""
    monkeypatch.chdir(tmp_path)

    # Criar estrutura mínima para passar checks básicos
    (tmp_path / ".buildtovalue/ledger.jsonl").write_text(
        '{"timestamp":"2025-12-01T00:00:00Z","task":"test","status":"success"}\n')
    (tmp_path / ".buildtovalue/archives").mkdir(parents=True)
    (tmp_path / ".buildtovalue/compliance").mkdir(parents=True)

    # Executar scan
    result = subprocess.run(
        ["bash", "scripts/compliance/unified-compliance-scanner.sh", "scan"],
        cwd=tmp_path,
        capture_output=True,
        text=True
    )

    # Verificar saída JSON
    try:
        scans = json.loads(result.stdout)
        assert isinstance(scans, list)
        assert len(scans) >= 3  # GDPR, SOX, ISO27001
    except json.JSONDecodeError:
        pytest.fail("Saída não é JSON válido")


def test_unified_report_generation(tmp_path, monkeypatch):
    """Verifica geração de relatório unificado"""
    monkeypatch.chdir(tmp_path)

    # Criar estrutura mínima
    (tmp_path / ".buildtovalue/ledger.jsonl").write_text(
        '{"timestamp":"2025-12-01T00:00:00Z","task":"test","status":"success"}\n')
    (tmp_path / ".buildtovalue/archives").mkdir(parents=True)

    result = subprocess.run(
        ["bash", "scripts/compliance/unified-compliance-scanner.sh", "report"],
        cwd=tmp_path,
        capture_output=True,
        text=True
    )

    # Verificar arquivo de relatório
    report_files = list((tmp_path / ".buildtovalue/compliance/reports").glob("unified-compliance-*.json"))
    assert len(report_files) > 0

    with open(report_files[0]) as f:
        report = json.load(f)

    assert "report_type" in report
    assert report["report_type"] == "Unified Compliance Assessment"
    assert "frameworks" in report
    assert "summary" in report


def test_certification_packager(tmp_path, monkeypatch):
    """Verifica empacotamento de evidências"""
    monkeypatch.chdir(tmp_path)

    # Criar evidências de teste
    (tmp_path / ".buildtovalue/ledger.jsonl").write_text("test\n")
    (tmp_path / ".buildtovalue/compliance/gdpr-data-inventory.json").write_text('{"test": true}')

    result = subprocess.run(
        ["bash", "scripts/compliance/certification-packager.sh", "collect", "gdpr"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=True
    )

    # Verificar package criado
    packages = list((tmp_path / ".buildtovalue/compliance/certification-packages").glob("gdpr-evidence-*.tar.gz"))
    assert len(packages) > 0


def test_package_validation(tmp_path, monkeypatch):
    """Verifica validação de integridade de packages"""
    monkeypatch.chdir(tmp_path)

    # Criar package de teste
    package_dir = tmp_path / ".buildtovalue/compliance/certification-packages/test-evidence"
    package_dir.mkdir(parents=True)

    test_file = package_dir / "test.txt"
    test_file.write_text("test content")

    # Criar checksum
    checksum = subprocess.run(
        ["sha256sum", str(test_file)],
        capture_output=True,
        text=True,
        check=True
    )

    checksum_file = package_dir / "test.txt.sha256"
    checksum_file.write_text(checksum.stdout.split()[0])

    # Comprimir
    package_file = tmp_path / ".buildtovalue/compliance/certification-packages/test-evidence.tar.gz"
    subprocess.run(
        ["tar", "czf", str(package_file), "-C", str(package_dir.parent), "test-evidence"],
        check=True
    )

    # Validar
    result = subprocess.run(
        ["bash", "scripts/compliance/certification-packager.sh", "validate", str(package_file)],
        cwd=tmp_path,
        capture_output=True,
        text=True
    )

    assert result.returncode == 0
    assert "Package válido" in result.stdout
