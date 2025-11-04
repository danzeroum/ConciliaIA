from pathlib import Path
from src.ethics.pii_detector import PIIDetector

def test_detects_cpf(tmp_path: Path):
    f = tmp_path / "demo.py"
    f.write_text("cpf = '123.456.789-10'")
    det = PIIDetector()
    m = det.scan_file(f)
    assert any(x.pii_type == "cpf" for x in m)
