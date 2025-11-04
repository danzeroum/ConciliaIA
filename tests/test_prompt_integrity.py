#!/usr/bin/env python3
"""
BuildToValue v7.4-Platinum
Testes de Integridade de Prompts (MPAA + Assinaturas)
----------------------------------------------------
Executa validação governada para assinatura e verificação de integridade
de prompts (hashes e validações MPAA).
"""

import os
import subprocess
from pathlib import Path


def test_prompt_signer_generates_valid_hash(tmp_path, monkeypatch):
    """✅ Gera hash de prompt válido via prompt-signer.py"""
    os.chdir(tmp_path)
    audit_dir = tmp_path / ".buildtovalue/audit"
    audit_dir.mkdir(parents=True)

    prompt = "Criar função de autenticação segura"

    # Caminho absoluto do script
    project_root = Path(__file__).resolve().parent.parent
    script_path = project_root / "scripts" / "governance" / "prompt-signer.py"

    result = subprocess.run(
        ["python3", str(script_path), prompt],
        capture_output=True, text=True, check=True
    )

    assert result.returncode == 0, f"Erro ao executar prompt-signer: {result.stderr}"
    output = result.stdout.strip()
    assert len(output) == 64, f"Hash inválido gerado: {output}"
    print("✅ Hash gerado com sucesso:", output)


def test_mpaa_rejects_tampered_prompt(tmp_path):
    """✅ MPAA rejeita prompt adulterado (governado)"""
    os.chdir(tmp_path)
    reports = tmp_path / ".buildtovalue/reports"
    reports.mkdir(parents=True)

    gen = reports / "gen.txt"
    audit = reports / "audit.txt"
    result_file = reports / "result.json"

    gen.write_text("print('hello')")
    audit.write_text("print('hello')")

    fake_hash = "a" * 64

    # Caminho absoluto do script de validação
    project_root = Path(__file__).resolve().parent.parent
    validator_path = project_root / "scripts" / "governance" / "mpaa-validator.py"

    result = subprocess.run(
        ["python3", str(validator_path), str(gen), str(audit), str(result_file), fake_hash],
        capture_output=True, text=True
    )

    # O validador deve retornar erro (status != 0)
    assert result.returncode != 0, "Validador deveria rejeitar prompt adulterado"
    assert result_file.exists(), "Arquivo de resultado deveria ser criado mesmo em falha"

    # Ler e validar conteúdo do resultado
    data = result_file.read_text().lower()

    # Aceita qualquer marcador de rejeição
    assert (
        '"status": "rejected"' in data
        or '"decision": "reject"' in data
        or '"valid": false' in data
    ), f"Conteúdo do resultado deveria indicar rejeição: {data}"

    print("✅ MPAA rejeitou prompt adulterado e gerou relatório de falha governado")


def test_prompt_integrity_batch_check(tmp_path, monkeypatch):
    """✅ Verifica assinatura de múltiplos prompts"""
    os.chdir(tmp_path)
    audit_dir = tmp_path / ".buildtovalue/audit"
    audit_dir.mkdir(parents=True)

    project_root = Path(__file__).resolve().parent.parent
    signer_path = project_root / "scripts" / "governance" / "prompt-signer.py"

    for i in range(3):
        prompt = f"Task {i}"
        result = subprocess.run(
            ["python3", str(signer_path), prompt],
            capture_output=True, text=True
        )
        assert result.returncode == 0, f"Falha ao assinar prompt {i}: {result.stderr}"
        hash_value = result.stdout.strip()
        assert len(hash_value) == 64
        print(f"✅ Prompt {i} assinado com hash {hash_value}")
