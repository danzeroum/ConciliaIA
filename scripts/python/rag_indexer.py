#!/usr/bin/env python3
"""
BuildToValue v7.0 - RAG Indexer
Indexes decisions into ChromaDB for Auto-RAG
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer


class Colors:
    GREEN = "\033[0;32m"
    BLUE = "\033[0;34m"
    YELLOW = "\033[1;33m"
    RED = "\033[0;31m"
    NC = "\033[0m"


def log_info(message: str) -> None:
    print(f"{Colors.BLUE}ℹ{Colors.NC} {message}")


def log_success(message: str) -> None:
    print(f"{Colors.GREEN}✓{Colors.NC} {message}")


def log_warn(message: str) -> None:
    print(f"{Colors.YELLOW}⚠{Colors.NC} {message}")


def log_error(message: str) -> None:
    print(f"{Colors.RED}✗{Colors.NC} {message}", file=sys.stderr)


class RAGIndexer:
    """RAG Indexer for BuildToValue decisions."""

    def __init__(
        self,
        chroma_host: str = "localhost",
        chroma_port: int = 8000,
        collection_name: str = "decisions",
        model_name: str = "all-MiniLM-L6-v2",
    ) -> None:
        log_info("Initializing RAG Indexer...")

        self.client = chromadb.HttpClient(
            host=chroma_host,
            port=chroma_port,
            settings=Settings(allow_reset=True),
        )

        self.collection_name = collection_name

        log_info(f"Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)

        try:
            self.collection = self.client.get_collection(collection_name)
            log_info(f"Using existing collection: {collection_name}")
        except Exception:
            self.collection = self.client.create_collection(
                name=collection_name,
                metadata={"hnsw:space": "cosine"},
            )
            log_success(f"Created new collection: {collection_name}")

    def read_decisions(self, source_path: str) -> List[Dict[str, Any]]:
        decisions: List[Dict[str, Any]] = []
        source = Path(source_path)

        if source.is_file():
            files = [source]
        elif source.is_dir():
            files = list(source.glob("**/*.jsonl"))
        else:
            log_error(f"Source not found: {source_path}")
            return decisions

        log_info(f"Reading decisions from {len(files)} file(s)...")

        for file in files:
            try:
                with file.open("r", encoding="utf-8") as handle:
                    for line_num, line in enumerate(handle, 1):
                        line = line.strip()
                        if not line:
                            continue
                        try:
                            decision = json.loads(line)
                            decisions.append(decision)
                        except json.JSONDecodeError as error:
                            log_warn(f"Invalid JSON in {file}:{line_num}: {error}")
            except Exception as error:
                log_error(f"Error reading {file}: {error}")

        log_success(f"Read {len(decisions)} decisions")
        return decisions

    def prepare_document(self, decision: Dict[str, Any]) -> str:
        parts: List[str] = []

        problem = decision.get("problem")
        if problem:
            parts.append(f"Problem: {problem}")

        context = decision.get("context")
        if context:
            if isinstance(context, dict):
                context_str = " ".join(str(value) for value in context.values())
                parts.append(f"Context: {context_str}")
            else:
                parts.append(f"Context: {context}")

        decision_info = decision.get("decision", {})
        rationale = decision_info.get("rationale") if isinstance(decision_info, dict) else None
        if rationale:
            parts.append(f"Rationale: {rationale}")

        outcome = decision.get("outcome", {})
        if isinstance(outcome, dict):
            lessons = outcome.get("lessons_learned")
            if lessons:
                parts.append(f"Lessons: {lessons}")

        return " ".join(parts)

    def generate_embedding(self, text: str) -> List[float]:
        embedding = self.model.encode(text, show_progress_bar=False)
        return embedding.tolist()

    def index_decisions(self, decisions: List[Dict[str, Any]], batch_size: int = 32) -> Dict[str, Any]:
        log_info(f"Indexing {len(decisions)} decisions...")

        indexed = 0
        skipped = 0
        errors = 0

        for start in range(0, len(decisions), batch_size):
            batch = decisions[start : start + batch_size]

            batch_ids: List[str] = []
            batch_embeddings: List[List[float]] = []
            batch_documents: List[str] = []
            batch_metadatas: List[Dict[str, Any]] = []

            for decision in batch:
                try:
                    decision_id = decision.get("id")
                    if not decision_id:
                        skipped += 1
                        continue

                    document = self.prepare_document(decision)
                    if not document:
                        skipped += 1
                        continue

                    embedding = self.generate_embedding(document)

                    metadata = {
                        "id": decision_id,
                        "timestamp": decision.get("timestamp", ""),
                        "problem_type": decision.get("problem_type", ""),
                        "ia": decision.get("routing", {}).get("primary_ia", ""),
                        "success": str(decision.get("execution", {}).get("success", False)),
                        "confidence": str(decision.get("routing", {}).get("confidence", 0)),
                    }

                    batch_ids.append(decision_id)
                    batch_embeddings.append(embedding)
                    batch_documents.append(document)
                    batch_metadatas.append(metadata)
                except Exception as error:
                    log_warn(f"Error processing decision {decision.get('id', 'unknown')}: {error}")
                    errors += 1

            if batch_ids:
                try:
                    self.collection.add(
                        ids=batch_ids,
                        embeddings=batch_embeddings,
                        documents=batch_documents,
                        metadatas=batch_metadatas,
                    )
                    indexed += len(batch_ids)
                    progress = min(start + batch_size, len(decisions))
                    print(f"\rIndexed: {progress}/{len(decisions)}", end="", flush=True)
                except Exception as error:
                    log_error(f"Error adding batch: {error}")
                    errors += len(batch_ids)

        if len(decisions) > 0:
            print()

        log_success("Indexing complete!")

        return {
            "total": len(decisions),
            "indexed": indexed,
            "skipped": skipped,
            "errors": errors,
        }

    def get_statistics(self) -> Dict[str, Any]:
        try:
            count = self.collection.count()
            return {
                "collection": self.collection_name,
                "total_documents": count,
                "embedding_model": self.model.get_sentence_embedding_dimension(),
                "distance_metric": "cosine",
            }
        except Exception as error:
            log_error(f"Error getting statistics: {error}")
            return {}

    def search(self, query: str, n_results: int = 5, min_similarity: float = 0.85) -> List[Dict[str, Any]]:
        try:
            query_embedding = self.generate_embedding(query)
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
            )

            formatted_results: List[Dict[str, Any]] = []

            ids = results.get("ids", [[]])[0]
            distances = results.get("distances", [[]])[0]
            documents = results.get("documents", [[]])[0]
            metadatas = results.get("metadatas", [[]])[0]

            for idx, doc_id in enumerate(ids):
                distance = distances[idx] if idx < len(distances) else 1.0
                similarity = 1 - distance
                if similarity < min_similarity:
                    continue

                document = documents[idx] if idx < len(documents) else ""
                metadata = metadatas[idx] if idx < len(metadatas) else {}

                formatted_results.append(
                    {
                        "id": doc_id,
                        "similarity": round(similarity, 3),
                        "document": document,
                        "metadata": metadata,
                    }
                )

            return formatted_results
        except Exception as error:
            log_error(f"Error searching: {error}")
            return []


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="BuildToValue v7.0 - RAG Indexer")
    parser.add_argument("command", choices=["index", "search", "stats"], help="Command to execute")
    parser.add_argument("--source", default=".buildtovalue/ledger/decisions", help="Source path for decisions")
    parser.add_argument("--query", help="Search query (for search command)")
    parser.add_argument("--max-results", type=int, default=5, help="Maximum number of search results")
    parser.add_argument("--threshold", type=float, default=0.85, help="Minimum similarity threshold for search")
    parser.add_argument("--batch-size", type=int, default=32, help="Batch size for indexing")
    parser.add_argument("--chroma-host", default="localhost", help="ChromaDB host")
    parser.add_argument("--chroma-port", type=int, default=8000, help="ChromaDB port")
    parser.add_argument("--model", default="all-MiniLM-L6-v2", help="Embedding model name")
    return parser


def main(argv: List[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        indexer = RAGIndexer(
            chroma_host=args.chroma_host,
            chroma_port=args.chroma_port,
            collection_name="decisions",
            model_name=args.model,
        )

        if args.command == "index":
            decisions = indexer.read_decisions(args.source)
            if not decisions:
                log_warn("No decisions found to index")
                return 1

            results = indexer.index_decisions(decisions, batch_size=args.batch_size)

            print()
            log_info("Results:")
            print(f"  Total:   {results['total']}")
            print(f"  Indexed: {results['indexed']}")
            if results["skipped"]:
                print(f"  Skipped: {results['skipped']}")
            if results["errors"]:
                print(f"  Errors:  {results['errors']}")

            return 0 if results["errors"] == 0 else 1

        if args.command == "search":
            if not args.query:
                log_error("--query is required for search command")
                return 1

            log_info(f"Searching for: {args.query}")
            results = indexer.search(args.query, n_results=args.max_results, min_similarity=args.threshold)

            if not results:
                log_warn("No results found")
                return 0

            print()
            log_success(f"Found {len(results)} result(s):")
            print()
            for idx, result in enumerate(results, 1):
                metadata = result.get("metadata", {})
                print(f"{idx}. {result['id']} (similarity: {result['similarity']})")
                print(f"   IA: {metadata.get('ia', 'unknown')}")
                print(f"   Success: {metadata.get('success', 'unknown')}")
                preview = result.get("document", "")[:100]
                print(f"   Preview: {preview}...")
                print()
            return 0

        if args.command == "stats":
            stats = indexer.get_statistics()
            if not stats:
                return 1

            print()
            log_info("Collection Statistics:")
            print(f"  Collection: {stats['collection']}")
            print(f"  Documents:  {stats['total_documents']}")
            print(f"  Model dim:  {stats['embedding_model']}")
            print(f"  Metric:     {stats['distance_metric']}")
            print()
            return 0

    except KeyboardInterrupt:
        print()
        log_info("Interrupted by user")
        return 130
    except Exception as error:  # pragma: no cover
        log_error(f"Fatal error: {error}")
        import traceback

        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
