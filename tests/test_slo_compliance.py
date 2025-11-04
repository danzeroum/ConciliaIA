#!/usr/bin/env python3
"""Testes de compliance de SLO/SLI."""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
SLI_CALCULATOR = REPO_ROOT / "scripts/slo/sli-calculator.sh"
SLO_REPORTER_MODULE = "scripts.slo.slo_reporter"


def test_slo_config_valid() -> None:
    slo_file = Path("scripts/slo/slos.yaml")
    assert slo_file.exists()

    import yaml  # type: ignore

    with slo_file.open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle)

    assert "slos" in config
    assert config["slos"], "Nenhum SLO definido"

    for slo in config["slos"]:
        assert "name" in slo
        assert "objective" in slo
        assert "target" in slo["objective"]


def test_success_rate_sli_calculation(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    ledger = tmp_path / ".buildtovalue" / "ledger.jsonl"
    ledger.parent.mkdir(parents=True)

    now = datetime.utcnow()
    for i in range(100):
        entry = {
            "timestamp": (now - timedelta(days=i % 20)).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "task": f"task-{i}",
            "result": "success" if i < 95 else "failure",
        }
        with ledger.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(entry) + "\n")

    result = subprocess.run(
        ["bash", str(SLI_CALCULATOR), "success-rate", "30"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=True,
    )
    success_rate = float(result.stdout.strip())
    assert 94.0 <= success_rate <= 96.0


def test_latency_p95_calculation(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    ledger = tmp_path / ".buildtovalue" / "ledger.jsonl"
    ledger.parent.mkdir(parents=True)

    now = datetime.utcnow()
    for i in range(100):
        entry = {
            "timestamp": (now - timedelta(days=i % 7)).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "task": f"task-{i}",
            "result": "success",
            "duration_seconds": i / 10.0,
        }
        with ledger.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(entry) + "\n")

    result = subprocess.run(
        ["bash", str(SLI_CALCULATOR), "latency-p95", "7"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=True,
    )
    p95 = float(result.stdout.strip())
    assert 9.0 <= p95 <= 10.0


def test_sli_report_generation(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    ledger_path = tmp_path / ".buildtovalue" / "ledger.jsonl"
    cost_path = tmp_path / ".buildtovalue" / "cost-ledger.jsonl"
    ledger_path.parent.mkdir(parents=True, exist_ok=True)
    ledger_path.touch()
    cost_path.touch()
    (tmp_path / ".buildtovalue" / "reports").mkdir(parents=True)

    slo_dir = tmp_path / "scripts" / "slo"
    slo_dir.mkdir(parents=True)
    shutil.copy(REPO_ROOT / "scripts/slo/slos.yaml", slo_dir / "slos.yaml")

    result = subprocess.run(
        ["bash", str(SLI_CALCULATOR), "report"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=True,
    )
    assert "BuildToValue v7.4 - SLI Report" in result.stdout
    assert "Task Success Rate" in result.stdout


def test_sli_json_export(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    ledger_path = tmp_path / ".buildtovalue" / "ledger.jsonl"
    cost_path = tmp_path / ".buildtovalue" / "cost-ledger.jsonl"
    ledger_path.parent.mkdir(parents=True, exist_ok=True)
    ledger_path.touch()
    cost_path.touch()
    (tmp_path / ".buildtovalue" / "slo-reports").mkdir(parents=True)

    subprocess.run(
        ["bash", str(SLI_CALCULATOR), "export"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=True,
    )

    export_files = list((tmp_path / ".buildtovalue" / "slo-reports").glob("slis-*.json"))
    assert export_files

    with export_files[0].open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    assert "timestamp" in data
    assert "slis" in data
    assert "task_success_rate_30d" in data["slis"]


def test_error_budget_calculation() -> None:
    sys.path.insert(0, str(REPO_ROOT))
    from scripts.slo.slo_reporter import SLOReporter

    reporter = SLOReporter()
    budget = reporter.calculate_error_budget(99.5, 99.6, 30)
    assert budget["error_budget_remaining"] > 0
    assert budget["status"] == "healthy"

    budget = reporter.calculate_error_budget(99.5, 98.0, 30)
    assert budget["error_budget_remaining"] <= 5
    assert budget["status"] == "critical"


def test_slo_text_report_generation(tmp_path: Path) -> None:
    slo_dir = tmp_path / ".buildtovalue" / "slo-reports"
    slo_dir.mkdir(parents=True)
    data = {
        "timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "slis": {
            "task_success_rate_30d": 99.6,
            "task_latency_p95_7d": 8.5,
            "mpaa_validation_accuracy_7d": 96.0,
            "cost_per_task_30d": 0.018,
        },
    }
    with (slo_dir / f"slis-{datetime.utcnow():%Y%m%d}.json").open("w", encoding="utf-8") as handle:
        json.dump(data, handle)

    sys.path.insert(0, str(REPO_ROOT))
    from scripts.slo.slo_reporter import SLOReporter

    reporter = SLOReporter(str(slo_dir))
    report = reporter.generate_text_report()
    assert "BuildToValue v7.4-Platinum" in report
    assert "99.6" in report


def test_slo_markdown_export(tmp_path: Path) -> None:
    slo_dir = tmp_path / ".buildtovalue" / "slo-reports"
    slo_dir.mkdir(parents=True)
    data = {
        "timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "slis": {
            "task_success_rate_30d": 99.6,
            "task_latency_p95_7d": 8.5,
            "mpaa_validation_accuracy_7d": 96.0,
            "cost_per_task_30d": 0.018,
        },
    }
    with (slo_dir / f"slis-{datetime.utcnow():%Y%m%d}.json").open("w", encoding="utf-8") as handle:
        json.dump(data, handle)

    sys.path.insert(0, str(REPO_ROOT))
    from scripts.slo.slo_reporter import SLOReporter

    reporter = SLOReporter(str(slo_dir))
    output_file = slo_dir / "test-report.md"
    md_content = reporter.export_markdown(str(output_file))
    assert output_file.exists()
    assert "# BuildToValue" in md_content
    assert "| SLO |" in md_content
