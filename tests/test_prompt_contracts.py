import sys
from pathlib import Path
import pytest

# Adiciona 'src' ao path para permitir importação do orquestrador
SRC_PATH = str(Path(__file__).resolve().parents[1] / "src")
if SRC_PATH not in sys.path:
    sys.path.append(SRC_PATH)

from orchestrator import IAOrchestrator


@pytest.fixture(scope="module")
def orchestrator_instance():
    """Instância única do orquestrador para testar seus métodos internos."""
    return IAOrchestrator()


@pytest.fixture
def mock_context():
    """Contexto simulado com o problema e respostas anteriores."""
    return {
        "problem": "Teste de API de Tarefas",
        "all_responses": [
            {"ia": "ia-business-analyst", "response": "Requisitos definidos..."},
            {"ia": "ia-arquiteto", "response": "Arquitetura definida..."}
        ]
    }


def test_ba_prompt_contract(orchestrator_instance, mock_context):
    prompt = orchestrator_instance._build_prompt("ia-business-analyst", "Definir", mock_context)
    assert "Você é um Analista de Negócios" in prompt
    assert "REQUISITOS FUNCIONAIS" in prompt
    assert "REQUISITOS NÃO-FUNCIONAIS" in prompt
    assert "ENTIDADES PRINCIPAIS" in prompt


def test_architect_prompt_contract(orchestrator_instance, mock_context):
    prompt = orchestrator_instance._build_prompt("ia-arquiteto", "Definir", mock_context)
    assert "Você é um Arquiteto de Software" in prompt
    assert "STACK TÉCNICO" in prompt
    assert "ESTRUTURA DO PROJETO" in prompt
    assert "ENDPOINTS API" in prompt
    assert "CONTEXTO ANTERIOR:" in prompt


def test_developer_prompt_contract(orchestrator_instance, mock_context):
    prompt = orchestrator_instance._build_prompt("ia-developer", "Codar", mock_context)
    assert "Você é um Desenvolvedor Python/FastAPI" in prompt
    assert "GERE CÓDIGO PYTHON COMPLETO E FUNCIONAL" in prompt
    assert "main.py" in prompt
    assert "models.py" in prompt
    assert "requirements.txt" in prompt
    assert "CONTEXTO COMPLETO:" in prompt


def test_qa_prompt_contract(orchestrator_instance, mock_context):
    prompt = orchestrator_instance._build_prompt("ia-qa", "Testar", mock_context)
    assert "Você é um Engenheiro de QA Python" in prompt
    assert "Crie testes pytest COMPLETOS" in prompt
    assert "fastapi.testclient import TestClient" in prompt
    assert "CONTEXTO:" in prompt
