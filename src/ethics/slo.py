from fastapi import APIRouter
import os
from typing import Dict

router = APIRouter(prefix="/ethics", tags=["ethics"])

# Metas SLO (30d) — ajustáveis por env
SLO_PII_MAX_30D = int(os.getenv("BTV_SLO_PII_MAX_30D", "1"))        # ≤ 1 exposição crítica/mês
SLO_BIAS_MAX_30D = int(os.getenv("BTV_SLO_BIAS_MAX_30D", "5"))       # ≤ 5 avisos severos/mês
SLO_FAIRNESS_MAX_30D = int(os.getenv("BTV_SLO_FAIR_MAX_30D", "3"))   # ≤ 3 violações de fairness/mês (placeholder)

def _slo_object() -> Dict:
    return {
        "targets_30d": {
            "pii_exposures_critical_max": SLO_PII_MAX_30D,
            "bias_warnings_severe_max": SLO_BIAS_MAX_30D,
            "fairness_violations_max": SLO_FAIRNESS_MAX_30D
        },
        "windows": {
            "trend_days": 7,
            "slo_days": 30
        },
        "guidance": {
            "pii": "Zero tolerance por sprint; máximo 1 exposição CRÍTICA a cada 30 dias.",
            "bias": "Avisos severos ≤ 5/mês; investigar disparidades >10%.",
            "fairness": "Violações ≤ 3/mês; reforçar testes de representatividade."
        }
    }

@router.get("/slo")
def get_ethics_slo():
    """
    Retorna as metas SLO e janelas usadas por Prometheus/Grafana.
    Métricas efetivas de cumprimento ficam nos dashboards/alertas (prometheus rules).
    """
    return {"ethics_slo": _slo_object()}
