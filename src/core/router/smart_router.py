"""Core routing logic for ConciliaAI v7."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

import numpy as np
import yaml
from sentence_transformers import SentenceTransformer

from src.learning.auto_rag import AutoRAG


@dataclass
class RoutingDecision:
    """Dataclass that represents the outcome of a routing request."""

    primary_ia: str
    support_ias: List[str]
    confidence: float
    reasoning: str
    conflict_risk: float
    estimated_cost: float
    escalate_human: bool
    similar_cases: List[Dict[str, Any]] = field(default_factory=list)


class SmartRouter:
    """Machine-learning assisted router that distributes work between personas."""

    PERSONA_DIRECTORY = Path(".buildtovalue/squad/personas")

    def __init__(self, ml_model: Optional[Any] = None, ml_enabled: bool = False) -> None:
        self.embedding_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
        self.personas = self.load_personas()
        self.rag = AutoRAG()
        self.ml_model = ml_model
        self.ml_enabled = ml_enabled and ml_model is not None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def route(self, problem: str, context: Dict[str, Any]) -> RoutingDecision:
        """Route a reconciliation problem to the most adequate persona."""

        if not self.personas:
            raise RuntimeError("No personas loaded for routing")

        problem_embedding = self.embedding_model.encode(problem)
        problem_type = self.classify_problem_type(problem, context)

        similar_cases = self.rag.search(query=problem, collection="decisions", top_k=5)

        ia_scores: Dict[str, float] = {}
        for ia_name, ia_config in self.personas.items():
            ia_scores[ia_name] = self.calculate_confidence(
                ia=ia_config,
                problem_type=problem_type,
                problem_embedding=problem_embedding,
                historical_success=self.get_success_rate(ia_name, problem_type, context),
                mental_model_match=self.match_mental_model(ia_config, problem_type, context),
                recent_performance=self.get_recent_perf(ia_name, context),
                cost_efficiency=self.get_cost_score(ia_name, context),
                similar_cases=similar_cases,
            )

        if self.ml_enabled:
            ia_scores = self.ml_model.adjust_scores(
                base_scores=ia_scores,
                context=context,
                historical_features=self.extract_features(similar_cases, problem_type),
            )

        top_ia = max(ia_scores, key=ia_scores.get)
        conflict_risk = self.predict_conflict(
            selected_ias=[top_ia],
            problem_type=problem_type,
            context=context,
        )

        support_ias = self.select_support(ia_scores, top_n=3, primary=top_ia)
        reasoning = self.generate_reasoning(ia_scores, similar_cases, problem_type)
        estimated_cost = self.estimate_cost(ia_scores, selected=top_ia)

        return RoutingDecision(
            primary_ia=top_ia,
            support_ias=support_ias,
            confidence=ia_scores[top_ia],
            reasoning=reasoning,
            conflict_risk=conflict_risk,
            estimated_cost=estimated_cost,
            escalate_human=ia_scores[top_ia] < 0.7,
            similar_cases=similar_cases,
        )

    # ------------------------------------------------------------------
    # Persona helpers
    # ------------------------------------------------------------------
    def load_personas(self) -> Dict[str, Dict[str, Any]]:
        personas: Dict[str, Dict[str, Any]] = {}
        if not self.PERSONA_DIRECTORY.exists():
            return personas

        for file in self.PERSONA_DIRECTORY.glob("*.yaml"):
            with file.open("r", encoding="utf-8") as handle:
                data = yaml.safe_load(handle) or {}
            identity = data.get("persona", {}).get("identity", {})
            name = identity.get("name") or file.stem
            personas[name] = data.get("persona", {})
        return personas

    # ------------------------------------------------------------------
    # Scoring helpers
    # ------------------------------------------------------------------
    def classify_problem_type(self, problem: str, context: Dict[str, Any]) -> str:
        text = f"{problem} {context.get('category', '')}".lower()
        if any(keyword in text for keyword in ("chargeback", "contest", "mdr")):
            return "financial_rules"
        if any(keyword in text for keyword in ("deploy", "infra", "pipeline")):
            return "platform"
        if any(keyword in text for keyword in ("parser", "integration", "api")):
            return "integration"
        if any(keyword in text for keyword in ("ux", "interface", "layout")):
            return "experience"
        return context.get("default_problem_type", "general")

    def calculate_confidence(
        self,
        ia: Dict[str, Any],
        problem_type: str,
        problem_embedding: np.ndarray,
        historical_success: float,
        mental_model_match: float,
        recent_performance: float,
        cost_efficiency: float,
        similar_cases: List[Dict[str, Any]],
    ) -> float:
        activation_score = self._semantic_alignment(ia, problem_embedding)
        rule_alignment = self._rule_alignment(ia, problem_type)

        weights = np.array([0.25, 0.2, 0.2, 0.15, 0.1, 0.1])
        features = np.array([
            activation_score,
            historical_success,
            mental_model_match,
            recent_performance,
            cost_efficiency,
            rule_alignment,
        ])
        raw_score = float(np.clip(np.dot(weights, features), 0.0, 1.0))

        # Boost when we found similar successful cases
        success_bias = 0.0
        for case in similar_cases:
            metadata = case.get("metadata", {})
            if metadata.get("ias", "").find(ia.get("identity", {}).get("name", "")) != -1:
                success_bias += 0.02
        return float(np.clip(raw_score + success_bias, 0.0, 1.0))

    def get_success_rate(self, ia_name: str, problem_type: str, context: Dict[str, Any]) -> float:
        metrics = (
            self.personas.get(ia_name, {})
            .get("performance_metrics", {})
        )
        if problem_type == "integration":
            lead_time = float(metrics.get("delivery_lead_time_days", 0.0))
            if lead_time <= 0:
                return 0.8
            return float(np.clip(1.0 / (1.0 + lead_time), 0.0, 1.0))
        if "accuracy" in metrics:
            return float(metrics.get("accuracy", 0.0))
        return float(metrics.get("average_confidence", 0.75))

    def match_mental_model(
        self,
        ia: Dict[str, Any],
        problem_type: str,
        context: Dict[str, Any],
    ) -> float:
        activation = ia.get("activation_triggers", {})
        semantic_patterns: Iterable[str] = activation.get("semantic_patterns", [])
        context_text = " ".join(str(value) for value in context.values()).lower()
        problem_lower = problem_type.lower()

        matches = sum(1 for pattern in semantic_patterns if pattern in context_text or pattern in problem_lower)
        if not semantic_patterns:
            return 0.5
        return float(np.clip(matches / len(list(semantic_patterns)), 0.0, 1.0))

    def get_recent_perf(self, ia_name: str, context: Dict[str, Any]) -> float:
        history: Dict[str, Dict[str, float]] = context.get("recent_performance", {})
        if ia_name in history:
            return float(history[ia_name].get("score", 0.0))
        metrics = (
            self.personas.get(ia_name, {})
            .get("performance_metrics", {})
        )
        return float(metrics.get("average_confidence", 0.8))

    def get_cost_score(self, ia_name: str, context: Dict[str, Any]) -> float:
        cost_context = context.get("cost", {})
        if ia_name in cost_context:
            return float(cost_context[ia_name])
        return 0.75

    def _semantic_alignment(self, ia: Dict[str, Any], problem_embedding: np.ndarray) -> float:
        activation = ia.get("activation_triggers", {})
        code_patterns = activation.get("code_patterns", [])
        if not code_patterns:
            return 0.6
        pattern_vector = self.embedding_model.encode(" ".join(code_patterns))
        return self._cosine_similarity(problem_embedding, pattern_vector)

    def _rule_alignment(self, ia: Dict[str, Any], problem_type: str) -> float:
        autonomy = ia.get("autonomy", {})
        approvals = autonomy.get("requires_approval", [])
        if not approvals:
            return 0.8
        matches = sum(1 for item in approvals if problem_type in item)
        return float(np.clip(1.0 - (matches / max(len(approvals), 1)), 0.0, 1.0))

    def _cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        a = np.asarray(a)
        b = np.asarray(b)
        denom = np.linalg.norm(a) * np.linalg.norm(b)
        if denom == 0:
            return 0.0
        return float(np.clip(np.dot(a, b) / denom, -1.0, 1.0))

    # ------------------------------------------------------------------
    # Advanced features
    # ------------------------------------------------------------------
    def extract_features(
        self, similar_cases: List[Dict[str, Any]], problem_type: str
    ) -> Dict[str, Any]:
        feature_vector = {
            "problem_type": problem_type,
            "cases_found": len(similar_cases),
            "avg_confidence": 0.0,
        }
        if similar_cases:
            confidences = [case.get("metadata", {}).get("confidence", 0.0) for case in similar_cases]
            feature_vector["avg_confidence"] = float(np.mean(confidences))
        return feature_vector

    def predict_conflict(
        self,
        selected_ias: List[str],
        problem_type: str,
        context: Dict[str, Any],
    ) -> float:
        escalations = context.get("recent_conflicts", 0)
        base = 0.1 * escalations
        diversity_penalty = 0.0
        if problem_type == "experience" and "ia-ethics-guardian" in selected_ias:
            diversity_penalty = 0.05
        return float(np.clip(base + diversity_penalty, 0.0, 1.0))

    def select_support(
        self, ia_scores: Dict[str, float], top_n: int, primary: str
    ) -> List[str]:
        ordered = sorted(
            ((name, score) for name, score in ia_scores.items() if name != primary),
            key=lambda item: item[1],
            reverse=True,
        )
        return [name for name, _ in ordered[:top_n]]

    def generate_reasoning(
        self,
        ia_scores: Dict[str, float],
        similar_cases: List[Dict[str, Any]],
        problem_type: str,
    ) -> str:
        top_entries = sorted(ia_scores.items(), key=lambda item: item[1], reverse=True)[:3]
        lines = [
            f"Top personas for {problem_type}:",
            *[f"- {name}: score={score:.2f}" for name, score in top_entries],
        ]
        if similar_cases:
            lines.append("Similar cases leveraged: " + ", ".join(case["id"] for case in similar_cases if case.get("id")))
        return "\n".join(lines)

    def estimate_cost(self, ia_scores: Dict[str, float], selected: str) -> float:
        confidence = ia_scores.get(selected, 0.0)
        return float(np.clip(1.0 - confidence, 0.0, 1.0))

    # ------------------------------------------------------------------
    # Utilities
    # ------------------------------------------------------------------
    @staticmethod
    def now() -> str:
        return datetime.now(timezone.utc).isoformat()

