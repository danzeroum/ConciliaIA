import os
import re


SCRIPT_NAME_PATTERN = re.compile(r"^[a-z0-9][a-z0-9._\-]*\.sh$")


def test_all_scripts_are_executable_and_named_correctly():
    """Verifica se todos os scripts possuem permissão +x e seguem convenção snake-case."""
    for root, _, files in os.walk("scripts"):
        for filename in files:
            if filename.endswith(".sh"):
                path = os.path.join(root, filename)
                assert os.access(path, os.X_OK), f"Script sem permissão +x: {path}"
                assert SCRIPT_NAME_PATTERN.match(filename), f"Nome inválido: {filename}"
