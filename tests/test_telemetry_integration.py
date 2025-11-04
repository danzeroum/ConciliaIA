#!/usr/bin/env python3
"""Testes de integração OpenTelemetry."""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
TRACER_SCRIPT = REPO_ROOT / "scripts/observability/tracer.py"
OTEL_COLLECTOR = REPO_ROOT / "scripts/observability/otel-collector.sh"
SPAN_EXPORTER = REPO_ROOT / "scripts/observability/span-exporter.sh"


def test_tracer_initialization() -> None:
    result = subprocess.run(
        ["python3", str(TRACER_SCRIPT)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "Tracer funcionando" in result.stdout or "OpenTelemetry não instalado" in result.stderr


def test_span_creation(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    telemetry_dir = tmp_path / ".buildtovalue" / "telemetry"
    telemetry_dir.mkdir(parents=True)

    test_script = tmp_path / "test_span.py"
    script_body = f"""
import sys
import time
sys.path.insert(0, {repr(str(REPO_ROOT))})
from scripts.observability.tracer import get_tracer

tracer = get_tracer()

with tracer.start_span('test.operation', attributes={{'test.key': 'value'}}):
    time.sleep(0.1)

print('SUCCESS')
"""
    test_script.write_text(script_body, encoding="utf-8")

    result = subprocess.run(["python3", str(test_script)], capture_output=True, text=True)
    assert "SUCCESS" in result.stdout or "OpenTelemetry não instalado" in result.stderr


def test_otel_collector_config_generation(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("BTV_OTEL_CONFIG_DIR", str(tmp_path / ".buildtovalue" / "telemetry"))

    subprocess.run(
        ["bash", str(OTEL_COLLECTOR), "generate-config"],
        capture_output=True,
        text=True,
        check=True,
    )

    config_file = tmp_path / ".buildtovalue" / "telemetry" / "otel-collector-config.yaml"
    assert config_file.exists()

    content = config_file.read_text(encoding="utf-8")
    assert "receivers:" in content
    assert "exporters:" in content
    assert "service:" in content


def test_span_export(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    traces_dir = tmp_path / ".buildtovalue" / "telemetry" / "traces"
    traces_dir.mkdir(parents=True)

    test_span = {"name": "test.span", "duration_ms": 100, "attributes": {"test": "value"}}
    (traces_dir / "test1.json").write_text(json.dumps([test_span]), encoding="utf-8")
    (traces_dir / "test2.json").write_text(json.dumps([test_span]), encoding="utf-8")

    subprocess.run(
        ["bash", str(SPAN_EXPORTER), "export"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=True,
    )

    export_file = tmp_path / ".buildtovalue" / "telemetry" / "spans-export.json"
    assert export_file.exists()
    spans = json.loads(export_file.read_text(encoding="utf-8"))
    assert len(spans) == 2


def test_trace_report_generation(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    spans_file = tmp_path / ".buildtovalue" / "telemetry" / "spans-export.json"
    spans_file.parent.mkdir(parents=True)

    test_spans = [
        {"name": "btv.task.execute", "duration_ms": 1500, "attributes": {"error": False}},
        {"name": "btv.task.execute", "duration_ms": 2000, "attributes": {"error": True, "error.type": "ValidationError"}},
    ]
    spans_file.write_text(json.dumps(test_spans), encoding="utf-8")

    result = subprocess.run(
        ["bash", str(SPAN_EXPORTER), "report", str(spans_file)],
        capture_output=True,
        text=True,
        check=True,
    )

    assert "Relatório de Traces" in result.stdout
    assert "btv.task.execute" in result.stdout
