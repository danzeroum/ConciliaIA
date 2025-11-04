import collections
import glob
import re


def test_no_duplicate_dependencies_across_files():
    """Garante que requirements.txt e requirements-dev.txt estão sincronizados sem versões conflitantes."""
    dependencies = collections.defaultdict(set)
    for file in glob.glob("requirements*.txt"):
        with open(file, encoding="utf-8") as handle:
            for line in handle:
                stripped = line.strip()
                if not stripped or stripped.startswith("#"):
                    continue
                if "==" in stripped or ">=" in stripped:
                    package = re.split(r"[><=]", stripped)[0]
                    dependencies[package].add(stripped)
    for package, versions in dependencies.items():
        assert (
            len(versions) == 1
        ), f"Dependência duplicada com versões diferentes: {package} -> {versions}"
