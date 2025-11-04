"""
Bias Analyzer - Detecta vieses em texto e contexto de decisão.
Parte do módulo IA-Ethics-Guardian.
"""

from collections import defaultdict
import re
from typing import Dict


class BiasAnalyzer:
    """Identifica indícios de vieses em um trecho de texto."""

    def __init__(self) -> None:
        # Dicionários básicos de termos sensíveis
        self.bias_keywords = {
            "gender": ["he", "she", "man", "woman"],
            "race": ["black", "white", "asian", "latino"],
            "age": ["young", "old", "senior", "millennial"],
            "socioeconomic": ["poor", "rich", "elite", "lower class"],
        }

    def analyze(self, text: str) -> Dict[str, object]:
        """Analisa o texto retornando risco agregado e ocorrências por categoria."""
        results = defaultdict(int)
        for category, keywords in self.bias_keywords.items():
            for word in keywords:
                matches = len(re.findall(rf"\b{re.escape(word)}\b", text, flags=re.IGNORECASE))
                if matches > 0:
                    results[category] += matches
        total_hits = sum(results.values())
        risk = min(1.0, total_hits / 10)  # risco proporcional
        return {"risk": risk, "details": dict(results)}
