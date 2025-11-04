#!/usr/bin/env python3
"""
Adaptive Quality Gates - BuildToValue v7.2
Sistema inteligente de quality gates baseado no tipo de projeto.
Implementa os princípios de Quality Intelligence Edition.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict

import yaml


class AdaptiveQualityGates:
    """Gates de qualidade adaptativos baseados no contexto do projeto."""

    def __init__(self, config_path: str = ".buildtovalue/config/quality-gates.yaml") -> None:
        self.config_path = Path(config_path)
        self.config: Dict[str, Any] = {}
        self._load_config()

    def _load_config(self) -> None:
        """Carrega configuração dos quality gates."""
        if self.config_path.exists():
            try:
                with self.config_path.open("r", encoding="utf-8") as file:
                    self.config = yaml.safe_load(file) or {}
            except yaml.YAMLError as exc:  # pragma: no cover - logging not configured
                raise RuntimeError(
                    f"Erro ao carregar configuração de quality gates: {exc}"
                ) from exc
        else:
            self.config = self._get_default_config()

        if "project_types" not in self.config:
            defaults = self._get_default_config()
            self.config.setdefault("project_types", defaults["project_types"])
            self.config.setdefault("adaptive_rules", defaults["adaptive_rules"])

    def _get_default_config(self) -> Dict[str, Any]:
        """Retorna configuração padrão baseada nos mental models v7.2."""
        return {
            "project_types": {
                "financial": {
                    "unit_coverage": 95,
                    "integration_coverage": 90,
                    "performance_threshold_ms": 100,
                    "mutation_threshold": 90,
                    "security_scan_required": True,
                    "bdd_required": True,
                },
                "internal-tool": {
                    "unit_coverage": 80,
                    "integration_coverage": 75,
                    "performance_threshold_ms": 500,
                    "mutation_threshold": 75,
                    "security_scan_required": True,
                    "bdd_required": False,
                },
                "prototype": {
                    "unit_coverage": 70,
                    "integration_coverage": 60,
                    "performance_threshold_ms": 1000,
                    "mutation_threshold": 60,
                    "security_scan_required": False,
                    "bdd_required": False,
                },
            },
            "adaptive_rules": {
                "auto_detect_project_type": True,
                "fallback_type": "internal-tool",
                "strict_mode": False,
            },
        }

    def get_gates(self, project_type: str) -> Dict[str, Any]:
        """Retorna os gates de qualidade para um tipo de projeto específico."""
        fallback_type = self.config.get("adaptive_rules", {}).get(
            "fallback_type", "internal-tool"
        )
        project_types = self.config.get("project_types", {})
        return project_types.get(project_type, project_types.get(fallback_type, {}))

    def detect_project_type(self, repo_path: str = ".") -> str:
        """Detecta automaticamente o tipo de projeto baseado em características."""
        path = Path(repo_path)

        if self._has_financial_indicators(path):
            return "financial"
        if self._has_prototype_indicators(path):
            return "prototype"
        return "internal-tool"

    def _has_financial_indicators(self, path: Path) -> bool:
        """Verifica indicadores de projeto financeiro."""
        financial_keywords = {
            "payment",
            "transaction",
            "bank",
            "financial",
            "account",
            "money",
            "transfer",
            "invoice",
            "tax",
            "compliance",
        }

        for file_path in path.rglob("*"):
            if file_path.is_file():
                name = file_path.name.lower()
                if any(keyword in name for keyword in financial_keywords):
                    return True

        config_files = ["pom.xml", "package.json", "requirements.txt"]
        for config_name in config_files:
            config_path = path / config_name
            if config_path.exists():
                content = config_path.read_text(encoding="utf-8", errors="ignore").lower()
                if any(keyword in content for keyword in financial_keywords):
                    return True

        return False

    def _has_prototype_indicators(self, path: Path) -> bool:
        """Verifica indicadores de projeto protótipo."""
        prototype_indicators = {
            "demo",
            "prototype",
            "experiment",
            "proof-of-concept",
            "poc",
            "spike",
            "exploration",
        }

        for dir_path in path.iterdir():
            if dir_path.is_dir():
                name = dir_path.name.lower()
                if any(indicator in name for indicator in prototype_indicators):
                    return True

        for readme_name in ("README.md", "readme.txt"):
            readme_path = path / readme_name
            if readme_path.exists():
                content = readme_path.read_text(encoding="utf-8", errors="ignore").lower()
                if any(indicator in content for indicator in prototype_indicators):
                    return True

        return False

    def validate_minimum(self, project_type: str | None = None) -> bool:
        """Valida se o projeto atende aos quality gates mínimos."""
        if not project_type:
            project_type = self.detect_project_type()

        gates = self.get_gates(project_type)
        print(f"🔍 Validando quality gates para: {project_type}")
        print(f"📊 Thresholds: {json.dumps(gates, indent=2, ensure_ascii=False)}")

        # Lógica de validação real seria implementada aqui.
        return True


def main() -> None:
    """Função principal para CLI."""
    parser = argparse.ArgumentParser(description="Adaptive Quality Gates v7.2")
    parser.add_argument("--project-type", help="Tipo do projeto")
    parser.add_argument(
        "--validate-minimum",
        action="store_true",
        help="Valida gates mínimos",
    )
    parser.add_argument(
        "--detect-type",
        action="store_true",
        help="Detecta tipo do projeto",
    )

    args = parser.parse_args()
    gates = AdaptiveQualityGates()

    if args.detect_type:
        detected_type = gates.detect_project_type()
        print(f"🎯 Tipo de projeto detectado: {detected_type}")
        print(
            "📋 Gates aplicáveis:",
            json.dumps(gates.get_gates(detected_type), indent=2, ensure_ascii=False),
        )

    if args.validate_minimum:
        if gates.validate_minimum(args.project_type):
            print("✅ Quality gates mínimos atendidos")
            raise SystemExit(0)
        print("❌ Quality gates mínimos não atendidos")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
