"""Smoke test for the /metrics endpoint using the global Prometheus registry."""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Dict

import anyio
import httpx
from prometheus_client import REGISTRY

# Ensure the repository root is importable when pytest runs in CI.
ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.main import app  # noqa: E402
from src.monitoring.metrics import (  # noqa: E402
    bias_warnings,
    bypass_attempts,
    code_coverage,
    contract_violations,
    flaky_test_rate,
    ia_response_time,
    mutation_score,
    pipeline_duration,
    pii_exposures,
    projects_generated,
    roi_per_project,
)


def _current_sample(metric: str, labels: Dict[str, str] | None = None) -> float:
    """Helper to get the current value of a metric sample from the global registry."""
    return REGISTRY.get_sample_value(metric, labels=labels) or 0.0


def test_metrics_endpoint_exposes_global_registry() -> None:
    async def _call_metrics() -> httpx.Response:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(
            transport=transport, base_url="http://testserver"
        ) as client:
            return await client.get("/metrics")

    # Capture baseline values to make the smoke test idempotent.
    baseline_projects = _current_sample("btv_projects_generated_total")
    baseline_contract_violations = _current_sample("btv_contract_violations_total")
    baseline_bypass = _current_sample(
        "btv_bypass_attempts_total", {"type": "override", "approved": "no"}
    )
    baseline_pii = _current_sample("btv_pii_exposures_total")
    baseline_bias = _current_sample(
        "btv_bias_warnings_total", {"category": "gender"}
    )

    # Business metrics
    projects_generated.inc()
    roi_per_project.labels(project_type="greenfield").set(1.5)

    # Technical metrics
    pipeline_duration.labels(stage="build", status="success").observe(2.0)
    ia_response_time.labels(ia_name="ia-developer", task_type="code-gen").observe(0.5)

    # Quality metrics
    code_coverage.labels(module="core").set(87.3)
    mutation_score.labels(module="core").set(72.1)
    flaky_test_rate.set(0.01)

    # Governance metrics
    contract_violations.inc()
    bypass_attempts.labels(type="override", approved="no").inc()

    # Ethics metrics
    pii_exposures.inc()
    bias_warnings.labels(category="gender").inc()

    response = anyio.run(_call_metrics)
    assert response.status_code == 200
    assert "text/plain" in response.headers["content-type"].lower()

    payload = response.text

    # Ensure the /metrics payload reflects the increments made through the global REGISTRY.
    assert "btv_projects_generated_total" in payload
    assert "btv_roi_per_project" in payload
    assert "btv_pipeline_duration_seconds" in payload
    assert "btv_ia_response_seconds" in payload
    assert "btv_code_coverage_percent" in payload
    assert "btv_mutation_score_percent" in payload
    assert "btv_flaky_test_rate" in payload
    assert "btv_contract_violations_total" in payload
    assert "btv_bypass_attempts_total" in payload
    assert "btv_pii_exposures_total" in payload
    assert "btv_bias_warnings_total" in payload

    # Validate that the Prometheus client recorded the expected totals via the global registry.
    assert (
        _current_sample("btv_projects_generated_total")
        == baseline_projects + 1.0
    )
    assert (
        _current_sample("btv_contract_violations_total")
        == baseline_contract_violations + 1.0
    )
    assert (
        _current_sample(
            "btv_bypass_attempts_total",
            {"type": "override", "approved": "no"},
        )
        == baseline_bypass + 1.0
    )
    assert _current_sample("btv_pii_exposures_total") == baseline_pii + 1.0
    assert (
        _current_sample("btv_bias_warnings_total", {"category": "gender"})
        == baseline_bias + 1.0
    )

    # Gauges should reflect the latest values set during the smoke test.
    assert (
        _current_sample("btv_roi_per_project", {"project_type": "greenfield"})
        == 1.5
    )
    assert (
        _current_sample("btv_code_coverage_percent", {"module": "core"})
        == 87.3
    )
    assert (
        _current_sample("btv_mutation_score_percent", {"module": "core"})
        == 72.1
    )
    assert _current_sample("btv_flaky_test_rate") == 0.01

    # Histograms expose both count and sum values.
    assert (
        _current_sample(
            "btv_pipeline_duration_seconds_sum",
            {"stage": "build", "status": "success"},
        )
        >= 2.0
    )
    assert (
        _current_sample(
            "btv_pipeline_duration_seconds_count",
            {"stage": "build", "status": "success"},
        )
        >= 1.0
    )
    assert (
        _current_sample(
            "btv_ia_response_seconds_sum",
            {"ia_name": "ia-developer", "task_type": "code-gen"},
        )
        >= 0.5
    )
    assert (
        _current_sample(
            "btv_ia_response_seconds_count",
            {"ia_name": "ia-developer", "task_type": "code-gen"},
        )
        >= 1.0
    )
