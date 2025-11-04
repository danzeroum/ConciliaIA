# src/monitoring/metrics.py
# BuildToValue v7.2 — Observability (REGISTRY global)
# Correção: remover CollectorRegistry isolado e usar REGISTRY global,
# garantindo que incrementos feitos em qualquer módulo apareçam no /metrics.

from fastapi import APIRouter, Response
from prometheus_client import (
    Counter,
    Histogram,
    Gauge,
    REGISTRY,
    generate_latest,
    CONTENT_TYPE_LATEST,
)

router = APIRouter()

# ────────────────────────────────────────────────────────────
# Métricas de Negócio
projects_generated = Counter(
    "btv_projects_generated_total", "Total de projetos gerados"
)
roi_per_project = Gauge(
    "btv_roi_per_project", "ROI por projeto", ["project_type"]
)

# ────────────────────────────────────────────────────────────
# Métricas Técnicas
pipeline_duration = Histogram(
    "btv_pipeline_duration_seconds", "Duração do pipeline", ["stage", "status"]
)
ia_response_time = Histogram(
    "btv_ia_response_seconds", "Tempo de resposta IA", ["ia_name", "task_type"]
)

# ────────────────────────────────────────────────────────────
# Métricas de Qualidade
code_coverage = Gauge(
    "btv_code_coverage_percent", "Code coverage", ["module"]
)
mutation_score = Gauge(
    "btv_mutation_score_percent", "Mutation test score", ["module"]
)
flaky_test_rate = Gauge(
    "btv_flaky_test_rate", "Taxa de testes flaky"
)

# ────────────────────────────────────────────────────────────
# Métricas de Governança
contract_violations = Counter(
    "btv_contract_violations_total", "Violações de contrato"
)
bypass_attempts = Counter(
    "btv_bypass_attempts_total", "Tentativas de bypass", ["type", "approved"]
)

# ────────────────────────────────────────────────────────────
# Métricas Éticas
pii_exposures = Counter(
    "btv_pii_exposures_total", "Exposições de PII detectadas"
)
bias_warnings = Counter(
    "btv_bias_warnings_total", "Avisos de bias", ["category"]
)

# ────────────────────────────────────────────────────────────
# Endpoint /metrics servindo o REGISTRY global
@router.get("/metrics")
def metrics() -> Response:
    data = generate_latest(REGISTRY)
    return Response(content=data, media_type=CONTENT_TYPE_LATEST)
