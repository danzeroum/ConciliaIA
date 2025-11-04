"""
Módulo avançado para extração de código dos outputs das IAs.
"""

import logging
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class CodeBlock:
    """Representa um bloco de código extraído"""

    language: str
    content: str
    file_path: Optional[str] = None
    line_start: Optional[int] = None
    line_end: Optional[int] = None


class CodeExtractor:
    """Extrai código estruturado de texto multibloco"""

    def __init__(self) -> None:
        self.supported_languages = {
            "python",
            "javascript",
            "typescript",
            "java",
            "go",
            "bash",
            "shell",
            "yaml",
            "yml",
            "json",
            "dockerfile",
            "sql",
            "html",
            "css",
            "markdown",
            "txt",
        }

    def extract_code_blocks(self, text: str) -> List[CodeBlock]:
        """
        Extrai TODOS os blocos de código (```language ... ```).

        Args:
            text: Texto completo com blocos de código

        Returns:
            Lista de CodeBlock com linguagem e conteúdo
        """

        blocks: List[CodeBlock] = []

        # Padrão para blocos de código com linguagem
        pattern = r"```(\w+)?\n(.*?)```"

        for match in re.finditer(pattern, text, re.DOTALL):
            language = match.group(1) or "text"
            content = match.group(2).strip()

            # Normaliza linguagem
            language = self._normalize_language(language)

            # Só adiciona se for uma linguagem suportada ou texto
            if language in self.supported_languages or language == "text":
                blocks.append(CodeBlock(language=language, content=content))
                logger.debug(
                    "Extraído bloco %s: %s caracteres", language, len(content)
                )

        # Também procura por blocos sem backticks mas com padrões de código
        blocks.extend(self._extract_implicit_blocks(text))

        logger.info("Extraídos %s blocos de código", len(blocks))
        return blocks

    def _normalize_language(self, language: str) -> str:
        """Normaliza nomes de linguagens"""

        language_map = {
            "py": "python",
            "js": "javascript",
            "ts": "typescript",
            "sh": "bash",
            "yaml": "yaml",
            "yml": "yaml",
            "docker": "dockerfile",
            "postgresql": "sql",
            "mysql": "sql",
        }
        return language_map.get(language.lower(), language.lower())

    def _extract_implicit_blocks(self, text: str) -> List[CodeBlock]:
        """Extrai blocos implícitos (sem backticks)"""

        blocks: List[CodeBlock] = []

        # Padrões para diferentes linguagens
        patterns = {
            "python": [
                r"(from \w+ import.*?(?=\n\n|\nclass|\ndef|\n@app|\nif __name__))",
                r"(class \w+.*?:\n.*?(?=\n\n|\nclass|\n@|\ndef|\Z))",
                r"(def \w+.*?:\n.*?(?=\n\n|\nclass|\ndef|\n@|\Z))",
                r"(import \w+(?:\.\w+)*(?:\s+as\s+\w+)?(?=\n\n|\nclass|\ndef|\Z))",
            ],
            "javascript": [
                r"(const\s+\w+\s*=.*?(?=\n\n|\nfunction|\nclass|\nconst|\nlet|\Z))",
                r"(function\s+\w+.*?(?=\n\n|\nfunction|\nclass|\nconst|\Z))",
                r"(class\s+\w+.*?(?=\n\n|\nfunction|\nclass|\nconst|\Z))",
            ],
            "yaml": [
                r"(---\n.*?\n\.\.\.(?=\n\n|\Z))",
                r"(\w+:\s*(?:\n\s+[\w-]+:.*?)+(?=\n\n|\Z))",
            ],
            "dockerfile": [
                r"(FROM\s+\w+.*?(?=\n\n|\nFROM|\Z))",
            ],
        }

        for lang, lang_patterns in patterns.items():
            for pattern in lang_patterns:
                for match in re.finditer(pattern, text, re.DOTALL):
                    content = match.group(1).strip()
                    if len(content) > 10:  # Mínimo de caracteres
                        blocks.append(CodeBlock(language=lang, content=content))

        return blocks

    def identify_file_paths(self, text: str) -> List[str]:
        """
        Identifica menções a arquivos no texto.

        Args:
            text: Texto para analisar

        Returns:
            Lista de caminhos de arquivo identificados
        """

        file_paths: List[str] = []

        # Padrões para identificação de arquivos
        patterns = [
            # ### 1. main.py
            r"###?\s*\d+\.?\s*([\w/-]+\.\w+)",
            # ## Arquivo: models.py
            r"##?\s*[Aa]rquivo:?\s*([\w/-]+\.\w+)",
            # 1. models.py
            r"\d+\.\s*([\w/-]+\.\w+)",
            # FILE: requirements.txt
            r"FILE:?\s*([\w/-]+\.\w+)",
            # "models.py"
            r'"([\w/-]+\.\w+)"',
            # 'database.py'
            r"'([\w/-]+\.\w+)'",
            # Caminhos com extensão
            r"\b[\w/-]+\.(py|js|ts|java|go|yaml|yml|json|txt|md|dockerfile|sql)\b",
        ]

        for pattern in patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                file_path = match.group(1) if match.groups() else match.group(0)
                # Normaliza caminho
                file_path = self._normalize_file_path(file_path)
                if file_path and file_path not in file_paths:
                    file_paths.append(file_path)

        # Remove duplicatas mantendo ordem
        seen = set()
        unique_paths: List[str] = []
        for path in file_paths:
            if path not in seen:
                seen.add(path)
                unique_paths.append(path)

        logger.info("Identificados %s arquivos: %s", len(unique_paths), unique_paths)
        return unique_paths

    def _normalize_file_path(self, file_path: str) -> str:
        """Normaliza caminho de arquivo"""

        # Remove espaços extras e caracteres inválidos
        file_path = file_path.strip().replace("\\", "/")

        # Remove prefixos comuns
        prefixes = ["file:", "arquivo:", "###", "##", "#", "*"]
        for prefix in prefixes:
            if file_path.lower().startswith(prefix.lower()):
                file_path = file_path[len(prefix) :].strip()

        # Garante que tem extensão
        if "." not in Path(file_path).name:
            return ""

        return file_path

    def match_code_to_files(
        self, code_blocks: List[CodeBlock], file_paths: List[str]
    ) -> Dict[str, str]:
        """
        Associa blocos de código aos arquivos correspondentes.

        Args:
            code_blocks: Lista de blocos de código extraídos
            file_paths: Lista de caminhos de arquivo identificados

        Returns:
            Dicionário {file_path: code_content}
        """

        files_map: Dict[str, str] = {}
        used_blocks: set[int] = set()

        # Estratégia 1: Busca por comentários no código
        for i, block in enumerate(code_blocks):
            if i in used_blocks:
                continue

            # Procura por menção a arquivo no conteúdo
            for file_path in file_paths:
                file_name = Path(file_path).name
                pattern = rf"#\s*(?:{re.escape(file_name)}|{re.escape(file_path)})"
                if re.search(pattern, block.content, re.IGNORECASE):
                    files_map[file_path] = block.content
                    used_blocks.add(i)
                    logger.debug("Associado %s por comentário", file_path)
                    break

        # Estratégia 2: Associação por ordem (1º bloco → 1º arquivo)
        remaining_blocks = [
            block for idx, block in enumerate(code_blocks) if idx not in used_blocks
        ]
        remaining_files = [file for file in file_paths if file not in files_map]

        for block, file_path in zip(remaining_blocks, remaining_files):
            files_map[file_path] = block.content
            used_blocks.add(code_blocks.index(block))
            logger.debug("Associado %s por ordem", file_path)

        # Estratégia 3: Inferência por tipo de arquivo vs linguagem
        file_ext_map = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".java": "java",
            ".go": "go",
            ".yaml": "yaml",
            ".yml": "yaml",
            ".json": "json",
            ".dockerfile": "dockerfile",
            ".sql": "sql",
            ".html": "html",
            ".css": "css",
            ".md": "markdown",
            ".txt": "text",
        }

        remaining_blocks = [
            block for idx, block in enumerate(code_blocks) if idx not in used_blocks
        ]
        remaining_files = [file for file in file_paths if file not in files_map]

        for file_path in remaining_files:
            ext = Path(file_path).suffix.lower()
            expected_lang = file_ext_map.get(ext)

            if expected_lang:
                # Encontra bloco com linguagem correspondente
                for block in remaining_blocks:
                    block_index = code_blocks.index(block)
                    if block_index in used_blocks:
                        continue
                    if block.language == expected_lang:
                        files_map[file_path] = block.content
                        used_blocks.add(block_index)
                        logger.debug(
                            "Associado %s por extensão (%s)", file_path, expected_lang
                        )
                        break

        logger.info("Associados %s arquivos com código", len(files_map))
        return files_map
