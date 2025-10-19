"""CLI helper used in CI to validate matching accuracy thresholds."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from typing import Dict, Sequence, Tuple

import asyncio

from tests.datasets.generate_test_dataset import generate_test_dataset, save_dataset
from tests.accuracy.test_reconciliation_accuracy import AccuracyMetrics, TestMatchingAccuracy
from src.application.services import MatchingService
from src.application.strategies import ExactMatcher, FuzzyMatcher, MLMatcher


def _compute_metrics(dataset: Dict[str, Sequence[dict]]) -> AccuracyMetrics:
    helper = TestMatchingAccuracy()
    matching_service = MatchingService(
        exact_matcher=ExactMatcher(),
        fuzzy_matcher=FuzzyMatcher(),
        ml_matcher=MLMatcher(model_path=None),
    )

    sales = helper._parse_sales(dataset["sales"])  # type: ignore[attr-defined]
    transactions = helper._parse_transactions(dataset["transactions"])  # type: ignore[attr-defined]

    loop = asyncio.new_event_loop()
    try:
        matches, _, _ = loop.run_until_complete(
            matching_service.match(list(sales), list(transactions))
        )
    finally:
        loop.close()

    metrics: AccuracyMetrics = helper._calculate_accuracy_metrics(  # type: ignore[attr-defined]
        matches=matches,
        ground_truth=dataset["ground_truth_matches"],
        total_sales=len(sales),
    )
    return metrics


def _load_dataset(path: Path, size: int) -> Dict[str, Sequence[dict]]:
    if path.exists():
        with path.open("r", encoding="utf-8") as handler:
            return json.load(handler)
    dataset = generate_test_dataset(size)
    save_dataset(dataset, path.name)
    with path.open("r", encoding="utf-8") as handler:
        return json.load(handler)


def main() -> Tuple[AccuracyMetrics, float]:
    parser = argparse.ArgumentParser(description="Validate reconciliation accuracy")
    parser.add_argument("--threshold", type=float, default=0.995)
    parser.add_argument("--dataset", type=int, default=10_000)
    parser.add_argument(
        "--path",
        type=Path,
        default=Path("tests/datasets/test_dataset_10k.json"),
    )
    args = parser.parse_args()

    dataset = _load_dataset(args.path, args.dataset)
    metrics = _compute_metrics(dataset)

    print(
        "Matching Accuracy Report\n"
        f"- Accuracy: {metrics.accuracy:.4%}\n"
        f"- Precision: {metrics.precision:.4f}\n"
        f"- Recall: {metrics.recall:.4f}\n"
        f"- False Positive Rate: {metrics.false_positive_rate:.4f}\n"
        f"- False Negative Rate: {metrics.false_negative_rate:.4f}"
    )

    if metrics.accuracy < args.threshold:
        raise SystemExit(1)

    return metrics, args.threshold


if __name__ == "__main__":
    main()
