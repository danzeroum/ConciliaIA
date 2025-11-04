#!/usr/bin/env python3
"""
BuildToValue v7.4-Platinum
Testes de manutenção e rotação do Ledger
--------------------------------------------------
Verifica rotação, limpeza e integridade dos arquivos
de ledger (governança do ciclo de vida dos registros).
"""

import os
import subprocess
import gzip
import time
from pathlib import Path


def test_ledger_rotates_when_exceeds_limit(tmp_path, monkeypatch):
    """✅ Verifica que ledger rotaciona ao exceder limite"""
    os.chdir(tmp_path)

    ledger_dir = tmp_path / ".buildtovalue/ledger"
    ledger_dir.mkdir(parents=True)

    # Criar ledger grande (> limite)
    ledger_file = ledger_dir / "ledger.jsonl"
    with ledger_file.open("w") as f:
        f.write("x" * 10_000_000)  # 10 MB fake data

    project_root = Path(__file__).resolve().parent.parent
    rotate_script = project_root / "scripts" / "maintenance" / "rotate-ledger.sh"

    result = subprocess.run(
        ["bash", str(rotate_script)],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, f"Falha ao rotacionar ledger: {result.stderr}"
    archives = list((tmp_path / ".buildtovalue/archives").glob("ledger-*.gz"))
    assert archives, "Nenhum arquivo de archive criado após rotação"
    print("✅ Ledger rotacionado com sucesso")


def test_archive_integrity_validation(tmp_path):
    """✅ Verifica validação de integridade de archives"""
    archive_dir = tmp_path / ".buildtovalue/archives"
    archive_dir.mkdir(parents=True)

    # Criar archive com hash
    archive_file = archive_dir / "ledger-20251104.jsonl.gz"
    hash_file = archive_dir / "ledger-20251104.jsonl.gz.sha256"

    data = "test data\n" * 100
    with gzip.open(archive_file, "wt") as f:
        f.write(data)

    result = subprocess.run(
        ["sha256sum", str(archive_file)],
        capture_output=True,
        text=True,
        check=True,
    )
    hash_value = result.stdout.split()[0]
    hash_file.write_text(hash_value)

    # Caminho absoluto do script
    project_root = Path(__file__).resolve().parent.parent
    checker_script = project_root / "scripts" / "maintenance" / "ledger-health-check.sh"

    verify_result = subprocess.run(
        ["bash", str(checker_script)],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )

    assert verify_result.returncode == 0, f"Verificação de integridade falhou: {verify_result.stderr}"
    print("✅ Integridade de archive validada")


def test_cleanup_old_archives(tmp_path, monkeypatch):
    """✅ Verifica limpeza de archives antigos"""
    archive_dir = tmp_path / ".buildtovalue/archives"
    archive_dir.mkdir(parents=True)

    monkeypatch.setenv("BTV_RETENTION_DAYS", "7")

    old_archive = archive_dir / "ledger-old.jsonl.gz"
    old_archive.touch()

    # Simular arquivo antigo (8 dias)
    old_time = time.time() - (8 * 24 * 60 * 60)
    os.utime(old_archive, (old_time, old_time))

    project_root = Path(__file__).resolve().parent.parent
    cleanup_script = project_root / "scripts" / "maintenance" / "cleanup-archives.sh"

    result = subprocess.run(
        ["bash", str(cleanup_script)],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, f"Falha na limpeza: {result.stderr}"
    assert not old_archive.exists(), "Arquivo antigo não foi removido"
    print("✅ Limpeza de archives antigos concluída")
