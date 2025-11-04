#!/usr/bin/env python3
"""Validações adicionais para perfis de seccomp."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

PROFILE_DIR = Path("scripts/security/seccomp-profiles")


def load_profile(name: str) -> dict:
    path = PROFILE_DIR / f"{name}.json"
    if not path.exists():
        pytest.skip(f"Perfil {name} inexistente")
    return json.loads(path.read_text(encoding="utf-8"))


def test_default_profile_has_allow_list() -> None:
    profile = load_profile("default")
    assert profile["defaultAction"] == "SCMP_ACT_ERRNO"
    allowed = next((item for item in profile["syscalls"] if item.get("action") == "SCMP_ACT_ALLOW"), None)
    assert allowed is not None
    assert "read" in allowed["names"]


def test_strict_profile_blocks_exec() -> None:
    profile = load_profile("strict")
    denied = [item for item in profile["syscalls"] if item.get("action") == "SCMP_ACT_ERRNO"]
    assert any("execve" in item.get("names", []) for item in denied)


def test_permissive_profile_allows_most_calls() -> None:
    profile = load_profile("permissive")
    assert profile["defaultAction"] == "SCMP_ACT_ALLOW"
    blocked_calls = [name for item in profile["syscalls"] for name in item.get("names", [])]
    assert "mount" in blocked_calls
