"""
Módulo para análise de artefatos gerados e métricas.
"""

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


@dataclass
class ArtifactsReport:
    """Relatório completo de análise de artefatos"""

    total_files: int
    total_lines: int
    languages: Dict[str, int]
    complexity: str
    ready_to_use: bool
    has_todos: bool
    file_types: Dict[str, int]
    estimated_development_time: str


class ArtifactsAnalyzer:
    """Analisa artefatos gerados e produz métricas"""

    def __init__(self) -> None:
        self.language_extensions = {
            ".py": "Python",
            ".js": "JavaScript",
            ".ts": "TypeScript",
            ".java": "Java",
            ".go": "Go",
            ".yaml": "YAML",
            ".yml": "YAML",
            ".json": "JSON",
            ".dockerfile": "Dockerfile",
            ".sql": "SQL",
            ".html": "HTML",
            ".css": "CSS",
            ".md": "Markdown",
            ".txt": "Text",
        }

    def analyze_artifacts(
        self, project_path: Path, ia_responses: List[Dict[str, Any]]
    ) -> ArtifactsReport:
        """
        Analisa artefatos gerados e produz relatório completo.

        Args:
            project_path: Caminho do projeto
            ia_responses: Respostas das IAs para contexto

        Returns:
            ArtifactsReport com métricas detalhadas
        """

        if not project_path.exists():
            return self._empty_report()

        # Coleta estatísticas
        total_files = 0
        total_lines = 0
        languages: Dict[str, int] = {}
        file_types: Dict[str, int] = {}
        has_todos = False

        for file_path in project_path.rglob("*"):
            if file_path.is_file():
                total_files += 1

                # Detecta linguagem
                lang = self.detect_language(file_path)
                languages[lang] = languages.get(lang, 0) + 1

                # Conta linhas
                lines = self.count_code_lines(file_path)
                total_lines += lines

                # Verifica TODOs
                if not has_todos:
                    has_todos = self._has_todos(file_path)

                # Tipo de arquivo
                ext = file_path.suffix.lower()
                file_types[ext] = file_types.get(ext, 0) + 1

        # Calcula complexidade
        complexity = self.estimate_complexity(total_lines, languages)

        # Verifica se está pronto
        ready_to_use = self.is_ready_to_use(project_path)

        # Tempo estimado
        dev_time = self.estimate_development_time(total_lines, complexity)

        return ArtifactsReport(
            total_files=total_files,
            total_lines=total_lines,
            languages=languages,
            complexity=complexity,
            ready_to_use=ready_to_use,
            has_todos=has_todos,
            file_types=file_types,
            estimated_development_time=dev_time,
        )

    def detect_language(self, file_path: Path) -> str:
        """Detecta linguagem por extensão do arquivo"""

        ext = file_path.suffix.lower()
        return self.language_extensions.get(ext, "Unknown")

    def count_code_lines(self, file_path: Path) -> int:
        """Conta linhas não-vazias e não-comentário"""

        try:
            with open(file_path, "r", encoding="utf-8") as handle:
                lines = handle.readlines()
        except Exception as exc:  # pragma: no cover - leitura inesperada
            logger.error("Erro ao contar linhas em %s: %s", file_path, exc)
            return 0

        code_lines = 0
        in_multiline_comment = False

        for line in lines:
            stripped = line.strip()

            # Ignora linhas vazias
            if not stripped:
                continue

            # Detecta comentários multi-linha
            if "\"\"\"" in line or "'''" in line:
                in_multiline_comment = not in_multiline_comment
                continue

            if in_multiline_comment:
                continue

            # Ignora comentários de linha
            if stripped.startswith(("#", "//", "--")):
                continue

            code_lines += 1

        return code_lines

    def _has_todos(self, file_path: Path) -> bool:
        """Verifica se arquivo tem TODOs ou FIXMEs"""

        try:
            with open(file_path, "r", encoding="utf-8") as handle:
                content = handle.read().lower()
        except Exception:  # pragma: no cover - leitura inesperada
            return False

        return any(marker in content for marker in ["todo", "fixme", "xxx", "hack"])

    def estimate_complexity(self, total_lines: int, languages: Dict[str, int]) -> str:
        """
        Estima complexidade do projeto.

        Args:
            total_lines: Total de linhas de código
            languages: Distribuição de linguagens

        Returns:
            'LOW', 'MEDIUM' ou 'HIGH'
        """

        # Fatores de complexidade
        line_factor = min(total_lines / 100, 3.0)  # 100 linhas = 1.0

        # Penalidade por múltiplas linguagens
        lang_factor = len(languages) * 0.5

        complexity_score = line_factor + lang_factor

        if complexity_score < 1.5:
            return "LOW"
        if complexity_score < 3.0:
            return "MEDIUM"
        return "HIGH"

    def is_ready_to_use(self, project_path: Path) -> bool:
        """
        Verifica se o projeto está pronto para uso.

        Args:
            project_path: Caminho do projeto

        Returns:
            True se o projeto está pronto
        """

        if not project_path.exists():
            return False

        files = [file.name for file in project_path.iterdir() if file.is_file()]

        # Verifica arquivos essenciais
        has_main = any(
            name in files for name in ["main.py", "app.py", "index.js", "index.ts"]
        )
        has_config = any(
            name in files for name in ["requirements.txt", "package.json", "Dockerfile"]
        )

        # Verifica se tem conteúdo significativo
        has_content = False
        for file_path in project_path.iterdir():
            if file_path.is_file() and file_path.stat().st_size > 50:
                has_content = True
                break

        return has_main and has_content

    def estimate_development_time(self, total_lines: int, complexity: str) -> str:
        """
        Estima tempo de desenvolvimento baseado em métricas.

        Args:
            total_lines: Total de linhas de código
            complexity: Complexidade do projeto

        Returns:
            String com tempo estimado
        """

        # Linhas por hora base (para complexidade LOW)
        base_lines_per_hour = 50

        # Ajusta por complexidade
        complexity_multiplier = {"LOW": 1.0, "MEDIUM": 1.5, "HIGH": 2.5}.get(
            complexity, 1.5
        )

        effective_lines_per_hour = base_lines_per_hour / complexity_multiplier

        if total_lines == 0:
            return "0 horas"

        hours = total_lines / effective_lines_per_hour

        if hours < 2:
            return f"{int(hours * 60)} minutos"
        if hours < 8:
            return f"{int(hours)} horas"

        days = hours / 8
        return f"{days:.1f} dias"

    def _empty_report(self) -> ArtifactsReport:
        """Retorna relatório vazio para projetos inexistentes"""

        return ArtifactsReport(
            total_files=0,
            total_lines=0,
            languages={},
            complexity="UNKNOWN",
            ready_to_use=False,
            has_todos=False,
            file_types={},
            estimated_development_time="0 horas",
        )

