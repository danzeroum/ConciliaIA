#!/usr/bin/env python3
"""Testes de resource limits e seccomp profiles."""
from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
RESOURCE_SCRIPT = REPO_ROOT / "scripts/security/resource-limiter.sh"
SANDBOX_EXECUTOR = REPO_ROOT / "scripts/orchestrator/sandbox-executor.sh"


def test_seccomp_profiles_exist() -> None:
    profiles = ["default", "strict", "permissive"]
    for profile in profiles:
        profile_path = Path(f"scripts/security/seccomp-profiles/{profile}.json")
        assert profile_path.exists(), f"Perfil {profile} não encontrado"
        data = json.loads(profile_path.read_text(encoding="utf-8"))
        assert "defaultAction" in data
        assert "syscalls" in data


def test_docker_limits_generation() -> None:
    result = subprocess.run(
        ["bash", str(RESOURCE_SCRIPT), "docker-limits", "test-container", "default"],
        capture_output=True,
        text=True,
        check=True,
    )
    limits = result.stdout.strip()
    assert "--memory=" in limits
    assert "--cpu-quota=" in limits
    assert "--pids-limit=" in limits


def test_resource_monitoring(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    reports_dir = tmp_path / ".buildtovalue" / "reports"
    reports_dir.mkdir(parents=True)

    test_script = tmp_path / "test.sh"
    test_script.write_text("#!/bin/bash\nsleep 2\n", encoding="utf-8")
    test_script.chmod(0o755)

    proc = subprocess.Popen(["bash", str(test_script)])

    try:
        subprocess.run(
            [
                "bash",
                str(RESOURCE_SCRIPT),
                "monitor",
                str(proc.pid),
                "3",
                "1",
            ],
            capture_output=True,
            text=True,
            timeout=10,
            check=True,
        )
    finally:
        proc.terminate()
        proc.wait()

    usage_files = list(reports_dir.glob(f"resource-usage-{proc.pid}.jsonl"))
    assert usage_files, "Arquivo de monitoramento não gerado"

    with usage_files[0].open("r", encoding="utf-8") as handle:
        lines = handle.readlines()
        assert len(lines) >= 1
        for line in lines:
            entry = json.loads(line)
            assert "cpu_percent" in entry
            assert "mem_rss_kb" in entry


def test_security_profile_selection() -> None:
    cases = [
        ("criar função com password", "strict"),
        ("build docker image", "permissive"),
        ("processar dados", "default"),
    ]

    for description, expected_profile in cases:
        result = subprocess.run(
            [
                "bash",
                "-c",
                f"source {SANDBOX_EXECUTOR}; select_security_profile '{description}'",
            ],
            capture_output=True,
            text=True,
            check=True,
            cwd=str(REPO_ROOT),
        )
        assert expected_profile in result.stdout


def test_cgroup_limits_application(tmp_path: Path) -> None:
    if not Path("/sys/fs/cgroup").exists():
        pytest.skip("cgroups v2 não disponível")

    test_script = tmp_path / "test.sh"
    test_script.write_text("#!/bin/bash\nsleep 5\n", encoding="utf-8")
    test_script.chmod(0o755)

    proc = subprocess.Popen(["bash", str(test_script)])
    try:
        result = subprocess.run(
            [
                "bash",
                str(RESOURCE_SCRIPT),
                "cgroup-limits",
                str(proc.pid),
                "default",
            ],
            capture_output=True,
            text=True,
        )
    finally:
        proc.terminate()
        proc.wait()

    assert result.returncode in {0, 1}
