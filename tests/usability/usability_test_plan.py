"""Structured plan to execute qualitative usability testing sessions."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List


@dataclass(frozen=True)
class UsabilityTask:
    id: str
    name: str
    scenario: str
    success_criteria: str
    metrics: List[str]


class UsabilityTestPlan:
    participants: int = 5
    duration_minutes: int = 30
    method: str = "Remote moderated (Zoom + Maze.co)"

    tasks: List[UsabilityTask] = [
        UsabilityTask(
            id="T1",
            name="Identify Financial Problem",
            scenario="Você acabou de fazer login no ConciliaAI. Há algum problema financeiro que você deveria saber?",
            success_criteria="Identificar 'R$ 2.347 perdidos' em < 10s",
            metrics=["time_on_task", "success_rate", "confidence_rating"],
        ),
        UsabilityTask(
            id="T2",
            name="Understand Divergence",
            scenario="Uma venda de R$ 1.200 aparece como problema. O que aconteceu?",
            success_criteria="Explicar com próprias palavras (compreensão)",
            metrics=["comprehension_score", "terminology_confusion"],
        ),
        UsabilityTask(
            id="T3",
            name="Recover Money (1-click)",
            scenario="Tente recuperar os R$ 1.200",
            success_criteria="Completar fluxo até confirmação em < 30s",
            metrics=["clicks_count", "time_on_task", "success_rate", "error_count"],
        ),
        UsabilityTask(
            id="T4",
            name="Multi-Store Comparison",
            scenario="Qual loja está com mais problemas financeiros?",
            success_criteria="Identificar 'Loja Sul' + explicar por quê",
            metrics=["time_on_task", "accuracy", "insight_quality"],
        ),
    ]

    questionnaires: Dict[str, List[str]] = {
        "pre_test": [
            "Qual sua experiência com sistemas de gestão financeira? (1-5)",
            "Com que frequência você reconcilia transações?",
            "Qual seu maior desafio com reconciliação hoje?",
        ],
        "post_task": [
            "Quão fácil foi completar essa tarefa? (1-5)",
            "Você se sentiu confiante durante a tarefa? (1-5)",
            "Algo te confundiu ou frustrou?",
        ],
        "post_test_sus": [
            "Eu acho que gostaria de usar este sistema frequentemente (1-5)",
            "Eu achei o sistema desnecessariamente complexo (1-5)",
            "Eu achei o sistema fácil de usar (1-5)",
            "Eu acho que precisaria de ajuda técnica para usar este sistema (1-5)",
            "Eu achei que as várias funções neste sistema estavam bem integradas (1-5)",
            "Eu achei que havia muita inconsistência neste sistema (1-5)",
            "Eu imagino que a maioria das pessoas aprenderia a usar este sistema rapidamente (1-5)",
            "Eu achei o sistema muito complicado de usar (1-5)",
            "Eu me senti muito confiante usando o sistema (1-5)",
            "Eu precisei aprender muitas coisas antes de usar este sistema (1-5)",
        ],
        "post_test_satisfaction": [
            "No geral, quão satisfeito você está com o sistema? (1-5)",
            "Você recomendaria este sistema para outros lojistas? (sim/não)",
            "O que você mais gostou?",
            "O que você mudaria ou melhoraria?",
            "Algum comentário adicional?",
        ],
    }


def calculate_sus_score(responses: List[int]) -> float:
    if len(responses) != 10:
        raise ValueError("SUS requires exactly 10 responses")

    score = 0
    for index in range(0, 10, 2):
        score += responses[index] - 1
    for index in range(1, 10, 2):
        score += 5 - responses[index]
    return score * 2.5


def run_usability_test_session(participant_id: str, profile: str) -> Dict[str, Any]:
    results: Dict[str, Any] = {
        "participant_id": participant_id,
        "profile": profile,
        "date": datetime.utcnow().isoformat(),
        "tasks": [],
        "sus_score": None,
        "satisfaction": None,
    }

    for task in UsabilityTestPlan.tasks:
        if task.id == "T4" and profile.lower() != "roberto":
            continue
        results["tasks"].append(
            {
                "task_id": task.id,
                "success": None,
                "time_seconds": None,
                "clicks": None,
                "errors": None,
                "notes": "",
            }
        )

    results_dir = Path("tests/usability/results")
    results_dir.mkdir(parents=True, exist_ok=True)
    output_file = results_dir / f"{participant_id}_results.json"

    import json

    with output_file.open("w", encoding="utf-8") as handler:
        json.dump(results, handler, indent=2, ensure_ascii=False)

    return results
