import sys
from pathlib import Path
import pytest
from unittest.mock import AsyncMock

# Adiciona 'src' ao path
SRC_PATH = str(Path(__file__).resolve().parents[1] / "src")
if SRC_PATH not in sys.path:
    sys.path.append(SRC_PATH)

# Importa FastAPI/TestClient e o app principal
try:
    from fastapi.testclient import TestClient
    from main import app
    from orchestrator import IAOrchestrator
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False

pytestmark = pytest.mark.skipif(not FASTAPI_AVAILABLE, reason="FastAPI ou TestClient não instalados")


@pytest.fixture
def client(monkeypatch):
    """Fixture do TestClient com mocks para IAOrchestrator."""
    mock_execute = AsyncMock(return_value={"status": "completed_mock"})
    monkeypatch.setattr(IAOrchestrator, "execute_routing", mock_execute)
    monkeypatch.setattr(IAOrchestrator, "_discover_ollama_url", lambda self: "http://mock-url:11434")
    with TestClient(app) as test_client:
        yield test_client


def test_api_health_check(client):
    response = client.get("/api/v7/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_api_route_contract_success(client):
    payload = {"problem": "Meu problema de teste"}
    response = client.post("/api/v7/orchestrator/route", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "routing_id" in data["data"]
    assert data["data"]["problem"] == "Meu problema de teste"


def test_api_route_contract_failure_422(client):
    payload = {"wrong_field": "valor"}
    response = client.post("/api/v7/orchestrator/route", json=payload)
    assert response.status_code == 422


def test_api_execute_contract_success(client):
    payload = {"routing_id": "RID-MOCK-123"}
    response = client.post("/api/v7/orchestrator/execute", json=payload)
    assert response.status_code == 200
    assert response.json()["data"]["status"] == "completed_mock"


def test_api_execute_contract_failure_422(client):
    payload = {}
    response = client.post("/api/v7/orchestrator/execute", json=payload)
    assert response.status_code == 422
