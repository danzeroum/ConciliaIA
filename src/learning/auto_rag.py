"""Auto-RAG engine that powers continuous learning for ConciliaAI."""
from __future__ import annotations

from typing import Dict, List

import chromadb
from sentence_transformers import SentenceTransformer


class AutoRAG:
    """Automatically manage retrieval-augmented data stores used by agents."""

    BASE_PATH = ".buildtovalue/learning/rag-collections"

    def __init__(self) -> None:
        self.client = chromadb.PersistentClient(path=self.BASE_PATH)
        self.embedding_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
        self.collections = {
            "lessons_learned": self.client.get_or_create_collection("lessons"),
            "decisions": self.client.get_or_create_collection("decisions"),
            "patterns": self.client.get_or_create_collection("patterns"),
        }

    # ------------------------------------------------------------------
    # Indexing helpers
    # ------------------------------------------------------------------
    def index_decision(self, decision: Dict[str, object]) -> None:
        """Index a decision artifact in the decisions collection."""

        document = self._decision_to_document(decision)
        embedding = self.embedding_model.encode(document).tolist()

        self.collections["decisions"].add(
            ids=[str(decision["id"])],
            embeddings=[embedding],
            metadatas=[
                {
                    "problem_type": decision.get("problem_type"),
                    "ias": ",".join(decision.get("ias_involved", [])),
                    "outcome": decision.get("outcome"),
                    "confidence": decision.get("confidence"),
                    "timestamp": decision.get("timestamp"),
                }
            ],
            documents=[document],
        )

    def capture_lesson_learned(self, lesson: Dict[str, object]) -> None:
        """Persist a lesson learned artifact for future retrieval."""

        document = self._lesson_to_document(lesson)
        embedding = self.embedding_model.encode(document).tolist()

        self.collections["lessons_learned"].add(
            ids=[str(lesson["id"])],
            embeddings=[embedding],
            metadatas=[
                {
                    "severity": lesson.get("severity"),
                    "category": lesson.get("category"),
                    "timestamp": lesson.get("timestamp"),
                }
            ],
            documents=[document],
        )

    # ------------------------------------------------------------------
    # Query helpers
    # ------------------------------------------------------------------
    def search(self, query: str, collection: str = "decisions", top_k: int = 5) -> List[Dict[str, object]]:
        """Perform semantic search across the configured collections."""

        if collection not in self.collections:
            raise ValueError(f"Collection '{collection}' not available in AutoRAG")

        query_embedding = self.embedding_model.encode(query).tolist()
        result = self.collections[collection].query(query_embeddings=[query_embedding], n_results=top_k)

        documents = result.get("documents", [[]])[0]
        metadatas = result.get("metadatas", [[]])[0]
        ids = result.get("ids", [[]])[0]
        distances = result.get("distances", [[]])[0]

        entries: List[Dict[str, object]] = []
        for idx, doc in enumerate(documents):
            entry = {
                "id": ids[idx],
                "document": doc,
                "metadata": metadatas[idx],
                "relevance": 1 - distances[idx] if idx < len(distances) else None,
            }
            entries.append(entry)
        return entries

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _decision_to_document(self, decision: Dict[str, object]) -> str:
        return (
            "Problem: {problem}\n"
            "Type: {problem_type}\n"
            "IAs: {ias}\n"
            "Approach: {approach}\n"
            "Outcome: {outcome}\n"
            "Reasoning: {reasoning}\n"
        ).format(
            problem=decision.get("problem", ""),
            problem_type=decision.get("problem_type", ""),
            ias=", ".join(decision.get("ias_involved", [])),
            approach=decision.get("approach", ""),
            outcome=decision.get("outcome", ""),
            reasoning=decision.get("reasoning", ""),
        )

    def _lesson_to_document(self, lesson: Dict[str, object]) -> str:
        patterns = ", ".join(lesson.get("reusable_patterns", []))
        return (
            "Trigger: {trigger}\n"
            "Problem: {problem}\n"
            "Root Cause: {root_cause}\n"
            "Resolution: {resolution}\n"
            "Prevention: {prevention}\n"
            "Patterns: {patterns}\n"
        ).format(
            trigger=lesson.get("trigger", ""),
            problem=lesson.get("problem", ""),
            root_cause=lesson.get("root_cause", ""),
            resolution=lesson.get("resolution", ""),
            prevention=lesson.get("prevention", ""),
            patterns=patterns,
        )

