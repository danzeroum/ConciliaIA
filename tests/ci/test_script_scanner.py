import os
import subprocess

def test_scanner_runs():
    assert os.path.exists("scripts/ci/scan-script-references.sh")
    cp = subprocess.run(
        ["bash", "-lc", "scripts/ci/scan-script-references.sh || true"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert "Candidatos à remoção" in cp.stdout
