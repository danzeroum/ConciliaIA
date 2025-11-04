# src/orchestrator.py
# BuildToValue v7.0 - Orquestrador Híbrido Otimizado

import asyncio
import logging
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple

import aiohttp
import requests
import yaml

logger = logging.getLogger(__name__)


class DecisionLedger:
    """Armazena entradas de decisão para auditoria."""

    def __init__(self) -> None:
        self.entries: List[Dict[str, Any]] = []

    def record(self, entry: Dict[str, Any]) -> None:
        self.entries.append(entry)

    def get_entries(self) -> List[Dict[str, Any]]:
        return list(self.entries)


class IAOrchestrator:
    """Orquestrador assíncrono otimizado para Ollama."""

    def __init__(self) -> None:
        # Paths e configurações centrais
        self.project_root = Path(__file__).resolve().parent.parent
        self.config_root = self.project_root / ".buildtovalue" / "config"
        self.contracts_dir = self.project_root / "docs" / "contracts"
        self.invariants_config = self._load_yaml_config("invariants.yaml")
        self.quality_gates_config = self._load_yaml_config("quality-gates.yaml")
        self.governance_config = self._load_yaml_config("governance.yaml")
        self._invariant_handlers = self._build_invariant_handlers()

        # ✅ URL FLEXÍVEL - Testa múltiplas opções
        self.ollama_url = self._discover_ollama_url()
        self.default_model = "llama3:latest"
        self.coding_model = "codellama:7b"
        self.timeout = aiohttp.ClientTimeout(total=60)  # timeout real de rede (60s)
        self.ledger = DecisionLedger()

    def _discover_ollama_url(self) -> str:
        """Descobre a URL funcional do Ollama."""

        possible_urls = [
            "http://localhost:11434",
            "http://host.docker.internal:11434",
            os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        ]

        for url in possible_urls:
            try:
                response = requests.get(f"{url}/api/version", timeout=5)
                if response.status_code == 200:
                    logger.info("✅ Ollama encontrado em: %s", url)
                    return url
            except Exception:  # pragma: no cover - rede externa
                continue

        logger.warning("⚠️  Não foi possível detectar Ollama, usando fallback")
        return "http://localhost:11434"

    async def execute_routing(self, routing_data: Dict[str, Any]) -> Dict[str, Any]:
        """Executar roteamento completo de forma assíncrona."""

        routing_id = routing_data.get("routing_id")
        problem = routing_data.get("problem", "")
        sequence = routing_data.get("sequence", [])

        logger.info("=" * 60)
        logger.info("🚀 INICIANDO EXECUÇÃO REAL")
        logger.info("📋 Problema: %s", problem)
        logger.info("🔢 Passos: %s", len(sequence))
        logger.info("=" * 60)

        results: List[Dict[str, Any]] = []
        context: Dict[str, Any] = {"problem": problem, "all_responses": []}
        success_count = 0

        for step in sequence:
            step_num = step.get("step")
            ia = step.get("ia")
            task = step.get("task")

            logger.info("\n▶️  PASSO %s/%s: %s", step_num, len(sequence), ia)
            logger.info("📌 Tarefa: %s", task)

            try:
                result = await self._call_ia_async(ia, task, context)

                if isinstance(result, str) and result.lstrip().upper().startswith("ERRO:"):
                    truncated = result[:300] + "..." if len(result) > 300 else result
                    results.append(
                        {
                            "step": step_num,
                            "ia": ia,
                            "task": task,
                            "result": truncated,
                            "status": "failed",
                            "timestamp": datetime.now().isoformat(),
                        }
                    )
                    if hasattr(self, "ledger") and hasattr(self.ledger, "record"):
                        self.ledger.record(
                            {
                                "event": "orchestration_step_failed",
                                "reason": "ia_returned_error_string",
                                "routing_id": routing_id,
                                "step": step_num,
                                "ia": ia,
                                "task": task,
                            }
                        )
                    logger.warning(
                        "⚠️  Passo %s retornou mensagem de erro legada: %s",
                        step_num,
                        truncated,
                    )
                else:
                    context["all_responses"].append(
                        {"ia": ia, "task": task, "response": result}
                    )

                    truncated = result[:300] + "..." if len(result) > 300 else result
                    results.append(
                        {
                            "step": step_num,
                            "ia": ia,
                            "task": task,
                            "result": truncated,
                            "status": "completed",
                            "timestamp": datetime.now().isoformat(),
                        }
                    )

                    success_count += 1

                    logger.info(
                        "✅ Passo %s concluído (%s caracteres)", step_num, len(result)
                    )

                    await asyncio.sleep(2)

            except Exception as exc:  # pragma: no cover - runtime safeguard
                logger.error("❌ Erro no passo %s: %s", step_num, exc)
                results.append(
                    {
                        "step": step_num,
                        "ia": ia,
                        "task": task,
                        "result": f"Erro: {exc}",
                        "status": "failed",
                        "timestamp": datetime.now().isoformat(),
                    }
                )
                if hasattr(self, "ledger") and hasattr(self.ledger, "record"):
                    self.ledger.record(
                        {
                            "event": "orchestration_step_failed",
                            "reason": type(exc).__name__,
                            "routing_id": routing_id,
                            "step": step_num,
                            "ia": ia,
                            "task": task,
                            "error": str(exc),
                        }
                    )

        artifacts = self._generate_artifacts(context)

        aggregate_text = "\n\n".join(
            response["response"] for response in context.get("all_responses", [])
        )
        invariants_report = self._validate_against_invariants(aggregate_text, context)
        quality_report = await self._execute_quality_gates(artifacts)
        requirements = self._extract_requirements(context)
        contracts_report = self._check_contract_compliance(
            requirements, artifacts, aggregate_text
        )

        logger.info("\n" + "=" * 60)
        logger.info("✅ EXECUÇÃO CONCLUÍDA")
        logger.info("=" * 60)

        return {
            "execution_id": f"EXEC-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            "status": "completed",
            "steps_completed": success_count,
            "total_steps": len(results),
            "results": results,
            "artifacts": artifacts,
            "summary": self._generate_summary(results),
            "governance": {
                "invariants": invariants_report,
                "quality_gates": quality_report,
                "contracts": contracts_report,
            },
        }

    async def _call_ia_async(self, ia_name: str, task: str, context: Dict[str, Any]) -> str:
        """Chamar IA via Ollama de forma assíncrona."""

        prompt = self._build_prompt(ia_name, task, context)
        model = self.coding_model if ia_name == "ia-developer" else self.default_model

        logger.info("🤖 Modelo: %s", model)
        logger.info("⏱️  Timeout configurado: 60s")

        payload: Dict[str, Any] = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.7, "num_predict": 1500},
        }

        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.post(
                    f"{self.ollama_url}/api/generate", json=payload
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        result = data.get("response", "").strip()
                        if not result:
                            raise RuntimeError("Resposta vazia do Ollama")
                        return result
                    error_text = await response.text()
                    raise RuntimeError(f"HTTP {response.status}: {error_text}")

        except asyncio.TimeoutError as exc:
            logger.error("⏱️  TIMEOUT!")
            raise asyncio.TimeoutError("Timeout - A IA ultrapassou 60 segundos.") from exc
        except aiohttp.ClientConnectorError as exc:
            logger.error("🔌 Erro de conexão com Ollama")
            raise RuntimeError("Falha de conexão com serviço de IA") from exc
        except Exception as exc:  # pragma: no cover - runtime safeguard
            logger.error("❌ Erro: %s", exc)
            raise

    def _build_prompt(self, ia_name: str, task: str, context: Dict[str, Any]) -> str:
        """Construir prompts otimizados mas simples."""

        problem = context.get("problem", "")
        previous = "\n\n".join(
            [
                f"[{resp['ia']}]: {resp['response'][:200]}..."
                for resp in context.get("all_responses", [])[-2:]
            ]
        )

        prompts: Dict[str, str] = {
            "ia-business-analyst": f"""Você é um Analista de Negócios.

PROBLEMA: {problem}

Analise e liste de forma clara:

## 1. REQUISITOS FUNCIONAIS (5-7 itens)
- Liste as funcionalidades necessárias

## 2. REQUISITOS NÃO-FUNCIONAIS (3-5 itens)
- Performance, segurança, usabilidade

## 3. ENTIDADES PRINCIPAIS (3-5 itens)
- Quais dados precisam ser armazenados?

## 4. CASOS DE USO (3-4 itens)
- Fluxos principais do sistema

Seja direto e técnico.""",
            "ia-arquiteto": f"""Você é um Arquiteto de Software especializado em FastAPI.

PROBLEMA: {problem}

CONTEXTO ANTERIOR:
{previous}

Defina a arquitetura técnica:

## 1. STACK TÉCNICO
- Backend: FastAPI
- Banco: SQLite
- Modelos: Pydantic + SQLAlchemy

## 2. ESTRUTURA DO PROJETO
```
projeto/
├── main.py          # FastAPI app
├── models.py        # Pydantic models
├── database.py      # SQLAlchemy setup
└── requirements.txt
```

## 3. MODELOS DE DADOS
Liste os modelos Pydantic necessários com campos

## 4. ENDPOINTS API
Liste os endpoints REST (CRUD)

Seja específico e técnico.""",
            "ia-developer": f"""Você é um Desenvolvedor Python/FastAPI experiente.

PROBLEMA: {problem}

CONTEXTO COMPLETO:
{previous}

GERE CÓDIGO PYTHON COMPLETO E FUNCIONAL.

Crie estes arquivos:

### 1. models.py
```python
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

# Defina os modelos Pydantic aqui
# Exemplo:
# class Cliente(BaseModel):
#     id: Optional[int] = None
#     nome: str
#     email: str
```

### 2. main.py
```python
from fastapi import FastAPI, HTTPException
from typing import List
import models

app = FastAPI()

# Banco em memória (simples)
database = []

@app.post("/api/items", response_model=models.Item)
def create_item(item: models.Item):
    # seu código CRUD aqui
    pass

# Implemente TODOS os endpoints CRUD
```

### 3. requirements.txt
```
fastapi==0.104.1
uvicorn==0.24.0
pydantic==1.10.13
```

IMPORTANTE:
- Código COMPLETO
- CRUD funcional
- Comentários em português
- Pronto para executar

Gere TODO o código agora.""",
            "ia-qa": f"""Você é um Engenheiro de QA Python.

PROBLEMA: {problem}

CONTEXTO:
{previous}

Crie testes pytest COMPLETOS:

```python
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_create_item():
    response = client.post("/api/items", json={{
        "nome": "Teste",
        "email": "teste@email.com"
    }})
    assert response.status_code == 200

def test_list_items():
    response = client.get("/api/items")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

# Adicione mais testes para:
# - GET por ID
# - PUT (update)
# - DELETE
# - Validações
```

Gere código de teste COMPLETO.""",
        }

        return prompts.get(ia_name, f"Execute: {task}\nProblema: {problem}")

    def _generate_artifacts(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Gerar artefatos baseados nas respostas das IAs."""

        try:
            from artifacts_analyzer import ArtifactsAnalyzer
            from code_extractor import CodeExtractor
            from project_generator import ProjectGenerator
        except Exception as exc:  # pragma: no cover - import dinâmico
            logger.error("Erro ao importar módulos auxiliares: %s", exc)
            return self._empty_artifacts(context.get("problem", "unknown"))

        all_responses = context.get("all_responses", [])
        if not all_responses:
            return self._empty_artifacts(context.get("problem", "unknown"))

        all_text = "\n\n".join(response["response"] for response in all_responses)

        extractor = CodeExtractor()
        code_blocks = extractor.extract_code_blocks(all_text)
        file_paths = extractor.identify_file_paths(all_text)
        files_map = extractor.match_code_to_files(code_blocks, file_paths)

        if not files_map:
            logger.warning("⚠️ Nenhum código foi extraído das respostas das IAs")
            return self._empty_artifacts(context.get("problem", "unknown"))

        project_name = self._sanitize_project_name(context.get("problem", ""))
        generator = ProjectGenerator()
        project = generator.create_project_structure(project_name, files_map)

        validation = generator.validate_project(project.root_path)

        analyzer = ArtifactsAnalyzer()
        report = analyzer.analyze_artifacts(project.root_path, all_responses)

        return {
            "project_name": project_name,
            "project_path": str(project.root_path),
            "code_blocks_found": len(code_blocks),
            "files_identified": list(files_map.keys()),
            "files_created": [
                str(path.relative_to(project.root_path)) for path in project.files_created
            ],
            "total_files": report.total_files,
            "total_lines": report.total_lines,
            "languages": report.languages,
            "complexity": report.complexity,
            "code_generated": bool(files_map),
            "ready_to_use": report.ready_to_use and validation.is_valid,
            "validation_issues": validation.issues,
            "has_todos": report.has_todos,
            "estimated_development_time": report.estimated_development_time,
            "file_types": report.file_types,
        }

    def _sanitize_project_name(self, problem: str) -> str:
        """Sanitiza nome do projeto para uso em caminhos."""

        import unicodedata

        name = unicodedata.normalize("NFKD", problem)
        name = name.encode("ASCII", "ignore").decode("ASCII")
        name = re.sub(r"[^\w\s-]", "", name.lower())
        name = re.sub(r"[-\s]+", "-", name)
        name = name[:30]
        return name.strip("-")

    def _empty_artifacts(self, problem: str) -> Dict[str, Any]:
        """Retorna artefatos vazios para fallback."""

        project_name = self._sanitize_project_name(problem)
        return {
            "project_name": project_name,
            "project_path": "",
            "code_blocks_found": 0,
            "files_identified": [],
            "files_created": [],
            "total_files": 0,
            "total_lines": 0,
            "languages": {},
            "complexity": "UNKNOWN",
            "code_generated": False,
            "ready_to_use": False,
            "validation_issues": ["Falha na extração de código"],
            "has_todos": False,
            "estimated_development_time": "0 horas",
            "file_types": {},
        }

    def _generate_summary(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Gerar resumo estruturado da execução."""

        total = len(results)
        completed = len([result for result in results if result["status"] == "completed"])
        success_rate = 0 if total == 0 else round((completed / total) * 100, 2)

        summary_text = f"""
╔══════════════════════════════════════╗
║   EXECUÇÃO CONCLUÍDA COM SUCESSO!    ║
╚══════════════════════════════════════╝

📊 Estatísticas:
   • Total de passos: {total}
   • Concluídos: {completed}
   • Taxa de sucesso: {success_rate:.0f}%

🤖 IAs Utilizadas:
"""
        for result in results:
            status_icon = "✅" if result["status"] == "completed" else "❌"
            summary_text += f"   {status_icon} {result['ia']}: {result['task']}\n"

        return {
            "text": summary_text.strip(),
            "total_steps": total,
            "completed_steps": completed,
            "success_rate": success_rate,
        }

    def _load_yaml_config(self, filename: str) -> Dict[str, Any]:
        """Carrega arquivos YAML de configuração padrão."""

        config_path = self.config_root / filename
        if not config_path.exists():
            logger.warning("Configuração %s não encontrada", config_path)
            return {}

        with config_path.open("r", encoding="utf-8") as handler:
            data = yaml.safe_load(handler) or {}
        return data if isinstance(data, dict) else {}

    def _build_invariant_handlers(self) -> Dict[str, Any]:
        """Mapeia regras conhecidas do invariants.yaml para validadores Python."""

        return {
            "no_sql_injection": self._check_no_sql_injection,
            "no_pii_in_logs": self._check_no_pii_in_logs,
            "no_empty_catch": self._check_no_empty_catch,
        }

    def _validate_against_invariants(self, code: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Valida respostas das IAs contra regras críticas definidas em invariants.yaml."""

        invariants = self.invariants_config.get("invariants", {})
        violations: List[Dict[str, Any]] = []
        evaluated = 0

        if not code.strip():
            return {
                "evaluated_rules": 0,
                "total_rules": 0,
                "violations": violations,
                "passed": True,
                "details": "Nenhum código fornecido para validação.",
            }

        for domain in invariants.values():
            for rule in domain.get("rules", []):
                rule_name = rule.get("name", "unknown")
                handler = self._invariant_handlers.get(rule_name)
                if handler is None:
                    continue
                evaluated += 1
                passed, message = handler(code)
                if not passed:
                    violations.append(
                        {
                            "rule": rule_name,
                            "severity": rule.get("severity", "warning"),
                            "message": message,
                        }
                    )

        return {
            "evaluated_rules": evaluated,
            "total_rules": sum(len(domain.get("rules", [])) for domain in invariants.values()),
            "violations": violations,
            "passed": not violations,
        }

    async def _execute_quality_gates(self, artifacts: Dict[str, Any]) -> Dict[str, Any]:
        """Executa quality gates críticos definidos em quality-gates.yaml."""

        policy = self.governance_config.get("quality_gates", {"enabled": False})
        if not policy.get("enabled", False):
            return {"enabled": False, "results": {}, "details": "Quality gates desabilitados."}

        gates_config = self.quality_gates_config.get("ia_quality_gates", {})
        selected_gates = ["flaky_test_rate", "confidence_accuracy"]
        results: Dict[str, Any] = {}

        for gate_name in selected_gates:
            gate = gates_config.get(gate_name)
            if gate is None:
                continue
            run_result = await self._run_gate_script(gate.get("command", ""))
            results[gate_name] = {
                "severity": gate.get("severity", "info"),
                "target": gate.get("target", ""),
                "status": run_result.get("status", "skipped"),
                "stdout": run_result.get("stdout", ""),
                "stderr": run_result.get("stderr", ""),
                "exit_code": run_result.get("exit_code"),
            }

        return {"enabled": True, "results": results, "artifacts_used": artifacts.get("files_identified", [])}

    async def _run_gate_script(self, command: str) -> Dict[str, Any]:
        """Executa scripts de gate em subprocesso assíncrono."""

        if not command:
            return {"status": "skipped", "stdout": "", "stderr": "Comando não definido."}

        process = await asyncio.create_subprocess_shell(
            command,
            cwd=str(self.project_root),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout_bytes, stderr_bytes = await process.communicate()
        stdout = stdout_bytes.decode().strip()
        stderr = stderr_bytes.decode().strip()

        return {
            "status": "passed" if process.returncode == 0 else "failed",
            "stdout": stdout,
            "stderr": stderr,
            "exit_code": process.returncode,
            "command": command,
        }

    def _extract_requirements(self, context: Dict[str, Any]) -> List[str]:
        """Extrai requisitos listados pela IA de Business Analyst."""

        for response in context.get("all_responses", []):
            if response.get("ia") != "ia-business-analyst":
                continue
            lines = [line.strip() for line in response.get("response", "").splitlines()]
            requirements = [
                line.lstrip("-• ")
                for line in lines
                if line.strip().startswith("-") or line.strip().startswith("•")
            ]
            return [req for req in requirements if req]
        return []

    def _check_contract_compliance(
        self,
        requirements: List[str],
        implementation: Dict[str, Any],
        implementation_text: str,
    ) -> Dict[str, Any]:
        """Valida conformidade com contratos e políticas de specification."""

        policy = self.governance_config.get("specification_policy", {})
        if not policy.get("enabled", False):
            return {
                "enforced": False,
                "compliant": True,
                "details": "Specification policy desabilitada (modo desenvolvimento).",
            }

        required_specs = policy.get("required_specs", [])
        missing_specs = [
            spec for spec in required_specs if not (self.contracts_dir / spec).exists()
        ]

        matched_requirements = [
            requirement
            for requirement in requirements
            if requirement.lower() in implementation_text.lower()
        ]
        coverage_ratio = (
            len(matched_requirements) / len(requirements) if requirements else 1.0
        )
        compliant = not missing_specs and coverage_ratio >= 0.8

        return {
            "enforced": True,
            "compliant": compliant,
            "coverage_ratio": round(coverage_ratio, 2),
            "missing_specs": missing_specs,
            "matched_requirements": matched_requirements,
            "implementation_files": implementation.get("files_identified", []),
        }

    def _check_no_sql_injection(self, code: str) -> Tuple[bool, str]:
        """Valida presença de padrões de concatenação insegura em SQL."""

        patterns = [
            r"SELECT\s+.+\+",
            r"INSERT\s+.+\+",
            r"UPDATE\s+.+\+",
            r"DELETE\s+.+\+",
            r"cursor\.execute\(f?\".*{",
        ]
        matches = [pattern for pattern in patterns if re.search(pattern, code, re.IGNORECASE)]
        if matches:
            return False, f"Concatenação de SQL detectada ({', '.join(matches)})"
        return True, ""

    def _check_no_pii_in_logs(self, code: str) -> Tuple[bool, str]:
        """Garante que dados sensíveis não sejam logados."""

        pii_terms = ["password", "senha", "cpf", "ssn", "creditcard", "cartao"]
        log_pattern = re.compile(r"log(?:ger)?\.(?:info|debug|warning|error)\((.*?)\)", re.IGNORECASE)
        violations: List[str] = []
        for match in log_pattern.finditer(code):
            statement = match.group(1).lower()
            if any(term in statement for term in pii_terms):
                violations.append(statement)
        if violations:
            return False, "Possível PII em logs: " + "; ".join(violations[:3])
        return True, ""

    def _check_no_empty_catch(self, code: str) -> Tuple[bool, str]:
        """Evita blocos de exceção vazios."""

        empty_catch_pattern = re.compile(r"except [^:]*:\s*(?:pass|...)", re.IGNORECASE)
        if empty_catch_pattern.search(code):
            return False, "Bloco de exceção vazio detectado."
        return True, ""
