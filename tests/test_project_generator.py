import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from project_generator import ProjectGenerator


class TestProjectGenerator:
    def setup_method(self) -> None:
        self.temp_dir = tempfile.mkdtemp()
        self.generator = ProjectGenerator(base_dir=Path(self.temp_dir))

    def test_create_project_structure(self) -> None:
        files = {
            "main.py": "print('hello')",
            "models.py": "class User:\n    pass",
        }
        project = self.generator.create_project_structure("test-project", files)

        assert project.root_path.exists()
        assert (project.root_path / "main.py").exists()
        assert (project.root_path / "models.py").exists()
        assert len(project.files_created) == 2

    def test_sanitize_project_name(self) -> None:
        name = self.generator._sanitize_project_name("My Test Project!")
        assert name == "my-test-project"

    def test_validate_project(self) -> None:
        files = {
            "main.py": "print('hello')",
            "requirements.txt": "fastapi\nuvicorn",
        }
        project = self.generator.create_project_structure("valid-project", files)
        validation = self.generator.validate_project(project.root_path)

        assert validation.is_valid
        assert len(validation.issues) == 0
