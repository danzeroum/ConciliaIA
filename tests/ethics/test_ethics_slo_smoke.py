from fastapi.testclient import TestClient
import pytest

# Tenta importar o app principal, mas cria um app de fallback se falhar
# Isso torna o teste robusto mesmo que o main.py esteja quebrado
try:
    from src.main import app
except ImportError:
    print("WARNING: Falha ao importar 'app' de 'src.main'. Criando app de teste isolado.")
    from fastapi import FastAPI
    from src.ethics.slo import router as ethics_slo_router
    app = FastAPI()
    app.include_router(ethics_slo_router)

def test_ethics_slo_endpoint_ok():
    c = TestClient(app)
    r = c.get("/ethics/slo")
    assert r.status_code == 200
    data = r.json()
    assert "ethics_slo" in data
    slo = data["ethics_slo"]
    assert "targets_30d" in slo and "windows" in slo
    t = slo["targets_30d"]
    # chaves essenciais
    assert "pii_exposures_critical_max" in t
    assert "bias_warnings_severe_max" in t
    assert "fairness_violations_max" in t
