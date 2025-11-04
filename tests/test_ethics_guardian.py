"""Testes para o módulo Ethics Guardian (bias e fairness)."""

from pathlib import Path
import sys

import pytest

ROOT_DIR = Path(__file__).resolve().parents[1]

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.ethics.bias_analyzer import BiasAnalyzer
from src.ethics.fairness_validator import FairnessValidator


def test_bias_detection():
    analyzer = BiasAnalyzer()
    result = analyzer.analyze("The young man led the team.")
    assert result["risk"] > 0
    assert "gender" in result["details"]


def test_fairness_score():
    validator = FairnessValidator()
    result = validator.assess({"male": 0.6, "female": 0.4})
    assert 0.7 < result["fairness_score"] <= 1.0
    assert result["difference"] == pytest.approx(0.2)
