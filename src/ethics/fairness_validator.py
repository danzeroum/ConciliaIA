"""
Fairness Validator - Avalia imparcialidade de decisões algorítmicas.
Parte do módulo IA-Ethics-Guardian.
"""

from typing import Dict


class FairnessValidator:
    """Avalia equilíbrio de distribuição entre grupos sensíveis."""

    def __init__(self) -> None:
        # Threshold padrão de desbalanceamento
        self.threshold = 0.2

    def assess(self, dataset_distribution: Dict[str, float]) -> Dict[str, float | bool]:
        """Avalia justiça com base na diferença percentual máxima entre grupos."""
        if not dataset_distribution:
            return {"fairness_score": 1.0, "balanced": True}

        values = list(dataset_distribution.values())
        diff = max(values) - min(values)
        fairness_score = max(0.0, 1.0 - diff)
        return {
            "fairness_score": fairness_score,
            "balanced": diff <= self.threshold,
            "difference": diff,
        }
