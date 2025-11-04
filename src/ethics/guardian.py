"""
Ethics Guardian - Orquestrador de checagens éticas.
Integra PII, Bias e Fairness Checkers.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, List, Optional

from .bias_analyzer import BiasAnalyzer
from .fairness_validator import FairnessValidator
from .pii_detector import PIIDetector

DEFAULT_SCAN_PATHS = ["src", "logs", "."]


def collect_files(paths: List[str]) -> List[Path]:
    """Coleta arquivos únicos a partir de uma lista de caminhos."""
    files: List[Path] = []
    for path_str in paths:
        base = Path(path_str)
        if base.is_file():
            files.append(base)
        elif base.is_dir():
            files.extend(f for f in base.rglob("*") if f.is_file())
    seen = set()
    unique: List[Path] = []
    for file_path in files:
        resolved = file_path.resolve()
        if resolved not in seen:
            unique.append(file_path)
            seen.add(resolved)
    return unique


class Guardian:
    """Orquestra verificações de PII, vieses e justiça algorítmica."""

    def __init__(self) -> None:
        self.pii = PIIDetector()
        self.bias = BiasAnalyzer()
        self.fairness = FairnessValidator()

    def review(
        self,
        text: str,
        dataset: Optional[Dict[str, float]] = None,
        *,
        pii_source: str = "input_text",
    ) -> Dict[str, Dict]:
        """Executa revisão ética completa sobre um texto e distribuição associada."""
        dataset = dataset or {}
        pii_report = self.pii.generate_report(self.pii.scan_text(text, source=pii_source))
        bias_report = self.bias.analyze(text)
        fairness_report = self.fairness.assess(dataset)
        return {"pii": pii_report, "bias": bias_report, "fairness": fairness_report}

    def scan_paths(self, paths: List[str]) -> Dict:
        """Executa detecção de PII em múltiplos caminhos."""
        matches = []
        for file_path in collect_files(paths):
            matches.extend(self.pii.scan_file(file_path))
        return self.pii.generate_report(matches)


def main() -> None:
    parser = argparse.ArgumentParser(description="Ethics Guardian - Aggregator (PII Scan)")
    parser.add_argument("--paths", nargs="*", default=DEFAULT_SCAN_PATHS, help="Caminhos a escanear")
    parser.add_argument("--output", default="reports/ethics-report.json", help="Arquivo de saída JSON")
    parser.add_argument("--fail-on-critical", action="store_true", help="Exit 1 se houver PII crítico")
    args = parser.parse_args()

    Path("reports").mkdir(parents=True, exist_ok=True)

    guardian = Guardian()
    report = guardian.scan_paths(args.paths)

    with open(args.output, "w", encoding="utf-8") as fo:
        json.dump(report, fo, indent=2, ensure_ascii=False)

    print(json.dumps(report, indent=2, ensure_ascii=False))

    if args.fail_on_critical and report["by_severity"]["critical"] > 0:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
