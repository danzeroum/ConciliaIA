"""
Módulo para geração de estrutura de projetos a partir de código extraído.
"""

import logging
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class ProjectStructure:
    """Estrutura de projeto gerada"""

    root_path: Path
    files_created: List[Path]
    readme_path: Optional[Path] = None


@dataclass
class ValidationResult:
    """Resultado da validação do projeto"""

    is_valid: bool
    issues: List[str]
    missing_files: List[str]


class ProjectGenerator:
    """Cria diretórios e salva arquivos de projeto"""

    def __init__(self, base_dir: Path = Path(".buildtovalue/generated")) -> None:
        self.base_dir = base_dir
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def create_project_structure(
        self, project_name: str, files: Dict[str, str]
    ) -> ProjectStructure:
        """
        Cria estrutura completa do projeto.

        Args:
            project_name: Nome do projeto
            files: Dicionário {file_path: content}

        Returns:
            ProjectStructure com informações do projeto criado
        """

        # Sanitiza nome do projeto
        safe_name = self._sanitize_project_name(project_name)
        project_path = self.base_dir / safe_name

        # Cria diretório principal
        project_path.mkdir(parents=True, exist_ok=True)
        logger.info("Criando projeto em: %s", project_path)

        files_created: List[Path] = []

        # Salva cada arquivo
        for file_rel_path, content in files.items():
            file_path = project_path / file_rel_path

            # Cria diretórios pais se necessário
            file_path.parent.mkdir(parents=True, exist_ok=True)

            # Salva conteúdo
            try:
                with open(file_path, "w", encoding="utf-8") as handle:
                    handle.write(content)
                files_created.append(file_path)
                logger.debug("Arquivo criado: %s", file_rel_path)
            except Exception as exc:  # pragma: no cover - falha de IO inesperada
                logger.error("Erro ao criar %s: %s", file_rel_path, exc)

        # Gera README se não existir
        readme_path = self._generate_readme(project_path, project_name, files)

        # Gera .gitignore se for projeto Python
        if any(path.suffix == ".py" for path in files_created):
            self._generate_gitignore(project_path)

        return ProjectStructure(
            root_path=project_path, files_created=files_created, readme_path=readme_path
        )

    def _sanitize_project_name(self, project_name: str) -> str:
        """
        Sanitiza nome do projeto para uso em caminhos de arquivo.

        Args:
            project_name: Nome original do projeto

        Returns:
            Nome sanitizado
        """

        import unicodedata

        # Remove acentos e caracteres especiais
        name = unicodedata.normalize("NFKD", project_name)
        name = name.encode("ASCII", "ignore").decode("ASCII")

        # Substitui espaços e caracteres inválidos
        name = re.sub(r"[^\w\s-]", "", name.lower())
        name = re.sub(r"[-\s]+", "-", name)

        # Limita tamanho
        name = name[:50]

        return name.strip("-")

    def _generate_readme(
        self, project_path: Path, project_name: str, files: Dict[str, str]
    ) -> Optional[Path]:
        """
        Gera README.md para o projeto.

        Args:
            project_path: Caminho do projeto
            project_name: Nome do projeto
            files: Arquivos do projeto

        Returns:
            Caminho do README criado ou None
        """

        readme_path = project_path / "README.md"

        # Se já existe README, não sobrescreve
        if readme_path.exists():
            return readme_path

        try:
            # Detecta tipo de projeto
            project_type = self._detect_project_type(files)

            readme_content = self._build_readme_content(
                project_name, project_type, files
            )

            with open(readme_path, "w", encoding="utf-8") as handle:
                handle.write(readme_content)

            logger.info("README gerado: %s", readme_path)
            return readme_path

        except Exception as exc:  # pragma: no cover - falha inesperada
            logger.error("Erro ao gerar README: %s", exc)
            return None

    def _detect_project_type(self, files: Dict[str, str]) -> str:
        """Detecta o tipo de projeto baseado nos arquivos"""

        file_names = [Path(file).name for file in files.keys()]

        if any(name.endswith(".py") for name in file_names):
            if "requirements.txt" in file_names or "setup.py" in file_names:
                return "python"
            return "python-script"
        if any(name.endswith((".js", ".ts")) for name in file_names):
            if "package.json" in file_names:
                return "nodejs"
            return "javascript"
        if any(name.endswith(".java") for name in file_names):
            return "java"
        if any(name.endswith(".go") for name in file_names):
            return "go"
        return "generic"

    def _build_readme_content(
        self, project_name: str, project_type: str, files: Dict[str, str]
    ) -> str:
        """Constrói conteúdo do README"""

        file_list = "\n".join([f"- `{file}`" for file in files.keys()])

        content = f"""# {project_name}

Projeto gerado automaticamente pelo BuildToValue v7.0

## 📁 Estrutura do Projeto

{file_list}

## 🚀 Como Executar

"""

        # Instruções específicas por tipo
        if project_type == "python":
            content += """
```bash
# Criar ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\\Scripts\\activate  # Windows

# Instalar dependências
pip install -r requirements.txt

# Executar
python main.py
```
"""
        elif project_type == "nodejs":
            content += """
```bash
# Instalar dependências
npm install

# Executar
npm start
```
"""
        else:
            content += """
Consulte a documentação específica de cada arquivo para instruções de execução.
"""

        content += f"""

## 📊 Métricas

- **Total de arquivos**: {len(files)}
- **Tipo de projeto**: {project_type}
- **Gerado em**: {self._get_current_timestamp()}

---

*Este projeto foi gerado automaticamente e pode precisar de ajustes manuais.*
"""
        return content

    def _generate_gitignore(self, project_path: Path) -> None:
        """Gera .gitignore para projetos Python"""

        gitignore_path = project_path / ".gitignore"
        if gitignore_path.exists():
            return

        gitignore_content = """# Virtual Environment
venv/
env/
.venv/

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# IDE
.vscode/
.idea/
*.swp
*.swo

# Logs
*.log
logs/

# Environment
.env
"""
        with open(gitignore_path, "w", encoding="utf-8") as handle:
            handle.write(gitignore_content)

    def _get_current_timestamp(self) -> str:
        """Retorna timestamp atual formatado"""

        from datetime import datetime

        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def validate_project(self, project_path: Path) -> ValidationResult:
        """
        Valida se o projeto é funcional.

        Args:
            project_path: Caminho do projeto

        Returns:
            ValidationResult com resultados da validação
        """

        issues: List[str] = []
        missing_files: List[str] = []

        if not project_path.exists():
            return ValidationResult(
                is_valid=False,
                issues=["Diretório do projeto não existe"],
                missing_files=[],
            )

        # Verifica arquivos essenciais por tipo
        files = [file.name for file in project_path.iterdir() if file.is_file()]

        # Verifica se tem arquivo principal
        main_files = [
            "main.py",
            "app.py",
            "index.js",
            "index.ts",
            "main.go",
            "Main.java",
        ]
        has_main = any(main in files for main in main_files)

        if not has_main:
            issues.append("Nenhum arquivo principal encontrado")
            missing_files.extend(main_files)

        # Verifica dependências
        if any(file.endswith(".py") for file in files) and "requirements.txt" not in files:
            issues.append("Projeto Python sem requirements.txt")
            missing_files.append("requirements.txt")

        # Verifica se arquivos não estão vazios
        for file_path in project_path.iterdir():
            if file_path.is_file() and file_path.stat().st_size == 0:
                issues.append(f"Arquivo vazio: {file_path.name}")

        is_valid = len(issues) == 0

        return ValidationResult(
            is_valid=is_valid, issues=issues, missing_files=missing_files
        )

