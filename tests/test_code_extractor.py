import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from code_extractor import CodeBlock, CodeExtractor


class TestCodeExtractor:
    def setup_method(self) -> None:
        self.extractor = CodeExtractor()

    def test_extract_python_blocks(self) -> None:
        text = """
        Here's some Python code:
        ```python
        def hello():
            return "world"
        ```
        And some more:
        ```py
        class Test:
            pass
        ```
        """
        blocks = self.extractor.extract_code_blocks(text)
        python_blocks = [block for block in blocks if block.language == "python"]
        assert len(python_blocks) >= 2
        assert "def hello():" in python_blocks[0].content

    def test_identify_file_paths(self) -> None:
        text = """
        ### 1. main.py
        ## Arquivo: models.py
        FILE: requirements.txt
        "config.yaml"
        """
        paths = self.extractor.identify_file_paths(text)
        assert "main.py" in paths
        assert "models.py" in paths
        assert "requirements.txt" in paths
        assert "config.yaml" in paths

    def test_match_code_to_files(self) -> None:
        blocks = [
            CodeBlock(language="python", content="# models.py\nclass User:\n    pass"),
            CodeBlock(language="python", content="def main():\n    pass"),
        ]
        files = ["models.py", "main.py"]
        result = self.extractor.match_code_to_files(blocks, files)
        assert "models.py" in result
        assert "main.py" in result
