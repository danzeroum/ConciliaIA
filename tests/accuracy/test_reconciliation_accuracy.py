"""Accuracy validation suite targeting 99.5% matching accuracy."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path
from typing import Dict, Iterable, List, Sequence

import pytest

from tests.datasets.generate_test_dataset import generate_test_dataset, save_dataset
from src.application.services import AnomalyDetectionService, MatchingService
from src.application.strategies import ExactMatcher, FuzzyMatcher, MLMatcher
from src.domain.entities import AcquirerTransaction, MatchType, ReconciliationMatch, Sale
from src.domain.value_objects import Money

DATASET_PATH = Path("tests/datasets/test_dataset_10k.json")


@dataclass(frozen=True)
class AccuracyMetrics:
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    true_positives: int
    false_positives: int
    false_negatives: int
    true_negatives: int
    false_positive_rate: float
    false_negative_rate: float


@pytest.fixture(scope="session")
def test_dataset_10k() -> Dict[str, Sequence[dict]]:
    """Provide the 10k dataset, generating it deterministically if needed."""

    if not DATASET_PATH.exists():
        dataset = generate_test_dataset(10_000)
        save_dataset(dataset, DATASET_PATH.name)
    with DATASET_PATH.open("r", encoding="utf-8") as handler:
        return json.load(handler)


@pytest.fixture(scope="session")
def reconciliation_system() -> tuple[MatchingService, AnomalyDetectionService]:
    matching_service = MatchingService(
        exact_matcher=ExactMatcher(),
        fuzzy_matcher=FuzzyMatcher(),
        ml_matcher=MLMatcher(model_path=None),
    )
    anomaly_service = AnomalyDetectionService()
    return matching_service, anomaly_service


class TestMatchingAccuracy:
    """Validate that the reconciliation pipeline achieves 99.5% accuracy."""

    @pytest.mark.critical
    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_overall_matching_accuracy_10k(
        self,
        test_dataset_10k: Dict[str, Sequence[dict]],
        reconciliation_system: tuple[MatchingService, AnomalyDetectionService],
    ) -> None:
        matching_service, _ = reconciliation_system

        sales = self._parse_sales(test_dataset_10k["sales"])
        transactions = self._parse_transactions(test_dataset_10k["transactions"])
        ground_truth = test_dataset_10k["ground_truth_matches"]

        matches, unmatched_sales, unmatched_txns = await matching_service.match_all(
            sales=list(sales),
            transactions=list(transactions),
        )

        metrics = self._calculate_accuracy_metrics(
            matches=matches,
            ground_truth=ground_truth,
            total_sales=len(sales),
        )

        assert metrics.accuracy >= 0.995, (
            f"Accuracy {metrics.accuracy:.4f} < 99.5% target | "
            f"false negatives={metrics.false_negatives} false positives={metrics.false_positives}"
        )
        assert metrics.false_positive_rate <= 0.01, (
            f"False positive rate {metrics.false_positive_rate:.4f} exceeds 1% threshold"
        )
        assert metrics.false_negative_rate <= 0.005, (
            f"False negative rate {metrics.false_negative_rate:.4f} exceeds 0.5% threshold"
        )

        assert not unmatched_sales, "All sales should be matched in synthetic dataset"
        assert not unmatched_txns, "All transactions should be matched in synthetic dataset"

    @pytest.mark.critical
    @pytest.mark.asyncio
    async def test_exact_matcher_100_percent(self) -> None:
        exact_matcher = ExactMatcher()

        sales: List[Sale] = []
        transactions: List[AcquirerTransaction] = []

        for index in range(100):
            nsu = f"EXACT{index:04d}"
            amount = Money(Decimal("100.00") + Decimal(index))
            txn_date = date(2025, 1, 15)

            sale = Sale(
                id=f"sale-{index}",
                tenant_id="test",
                nsu=nsu,
                amount=amount,
                date=txn_date,
                payment_method="credit_1x",
            )

            transaction = AcquirerTransaction(
                id=f"txn-{index}",
                tenant_id="test",
                acquirer="cielo",
                nsu=nsu,
                transaction_date=txn_date,
                amount=amount,
                mdr_amount=Money(amount.amount * Decimal("0.03")),
                net_amount=Money(amount.amount * Decimal("0.97")),
            )

            sales.append(sale)
            transactions.append(transaction)

        matches, unmatched_sales, unmatched_txns = await exact_matcher.match(
            sales=sales,
            transactions=transactions,
        )

        assert len(matches) == 100
        assert not unmatched_sales
        assert not unmatched_txns
        for match in matches:
            assert match.confidence == Decimal("1.0")
            assert match.match_type is MatchType.EXACT

    @pytest.mark.critical
    @pytest.mark.asyncio
    async def test_fuzzy_matcher_within_tolerance(self) -> None:
        fuzzy_matcher = FuzzyMatcher()

        test_cases = [
            (Decimal("100.00"), Decimal("100.00"), True),
            (Decimal("100.00"), Decimal("100.25"), True),
            (Decimal("100.00"), Decimal("99.75"), True),
            (Decimal("100.00"), Decimal("100.50"), True),
            (Decimal("100.00"), Decimal("99.50"), True),
            (Decimal("100.00"), Decimal("100.51"), False),
            (Decimal("100.00"), Decimal("99.49"), False),
        ]

        for sale_amount, txn_amount, should_match in test_cases:
            sale = Sale(
                id="sale-test",
                tenant_id="tenant-test",
                nsu="NSU123",
                amount=Money(sale_amount),
                date=date(2025, 1, 15),
                payment_method="credit_1x",
            )

            transaction = AcquirerTransaction(
                id="txn-test",
                tenant_id="tenant-test",
                acquirer="cielo",
                nsu="NSU123",
                transaction_date=date(2025, 1, 15),
                amount=Money(txn_amount),
                mdr_amount=Money(txn_amount * Decimal("0.03")),
                net_amount=Money(txn_amount * Decimal("0.97")),
            )

            matches, _, _ = await fuzzy_matcher.match([sale], [transaction])

            if should_match:
                assert matches, (
                    f"Expected a match for sale {sale_amount} vs transaction {txn_amount}"
                )
                assert matches[0].confidence >= Decimal("0.85")
            else:
                assert not matches, (
                    f"Expected no match for sale {sale_amount} vs transaction {txn_amount}"
                )

    def _parse_sales(self, payload: Iterable[dict]) -> List[Sale]:
        return [
            Sale(
                id=item["id"],
                tenant_id=item["tenant_id"],
                nsu=item["nsu"],
                amount=Money(Decimal(str(item["amount"]))),
                date=date.fromisoformat(item["date"]),
                payment_method=item["payment_method"],
                installments=item.get("installments", 1),
            )
            for item in payload
        ]

    def _parse_transactions(self, payload: Iterable[dict]) -> List[AcquirerTransaction]:
        return [
            AcquirerTransaction(
                id=item["id"],
                tenant_id=item["tenant_id"],
                acquirer=item["acquirer"],
                nsu=item["nsu"],
                amount=Money(Decimal(str(item["gross_amount"]))),
                transaction_date=date.fromisoformat(item["transaction_date"]),
                mdr_amount=Money(Decimal(str(item["mdr_fee"]))),
                net_amount=Money(Decimal(str(item["net_amount"]))),
            )
            for item in payload
        ]

    def _calculate_accuracy_metrics(
        self,
        matches: Sequence[ReconciliationMatch],
        ground_truth: Sequence[dict],
        total_sales: int,
    ) -> AccuracyMetrics:
        expected_lookup: Dict[str, set[str]] = {}
        for item in ground_truth:
            sale_id = item["sale_id"]
            if "transaction_id" in item:
                expected_lookup.setdefault(sale_id, set()).add(item["transaction_id"])

        true_positives = 0
        false_positives = 0

        for match in matches:
            expected_txns = expected_lookup.get(match.sale_id, set())
            if match.transaction_id in expected_txns:
                true_positives += 1
            else:
                false_positives += 1

        false_negatives = sum(len(txns) for txns in expected_lookup.values()) - true_positives
        true_negatives = max(total_sales - (true_positives + false_positives + false_negatives), 0)

        accuracy = (
            (true_positives + true_negatives) / total_sales if total_sales else 0.0
        )
        precision = (
            true_positives / (true_positives + false_positives)
            if (true_positives + false_positives)
            else 0.0
        )
        recall = (
            true_positives / (true_positives + false_negatives)
            if (true_positives + false_negatives)
            else 0.0
        )
        f1_score = (
            2 * (precision * recall) / (precision + recall)
            if (precision + recall)
            else 0.0
        )
        false_positive_rate = false_positives / total_sales if total_sales else 0.0
        false_negative_rate = false_negatives / total_sales if total_sales else 0.0

        return AccuracyMetrics(
            accuracy=accuracy,
            precision=precision,
            recall=recall,
            f1_score=f1_score,
            true_positives=true_positives,
            false_positives=false_positives,
            false_negatives=false_negatives,
            true_negatives=true_negatives,
            false_positive_rate=false_positive_rate,
            false_negative_rate=false_negative_rate,
        )


class TestAnomalyDetection:
    """Validate anomaly detection recall for missing transactions."""

    @pytest.mark.critical
    @pytest.mark.asyncio
    async def test_missing_transaction_detection_recall(
        self,
        test_dataset_10k: Dict[str, Sequence[dict]],
        reconciliation_system: tuple[MatchingService, AnomalyDetectionService],
    ) -> None:
        _, anomaly_service = reconciliation_system

        ground_truth = [
            item
            for item in test_dataset_10k["ground_truth_divergences"]
            if item["type"] == "missing_transaction"
        ]

        matched_sale_ids = {
            match["sale_id"]
            for match in test_dataset_10k["ground_truth_matches"]
        }

        unmatched_sales = [
            item
            for item in test_dataset_10k["sales"]
            if item["id"] not in matched_sale_ids
        ]

        unmatched_sale_entities = [
            Sale(
                id=item["id"],
                tenant_id=item["tenant_id"],
                nsu=item["nsu"],
                amount=Money(Decimal(str(item["amount"]))),
                date=date.fromisoformat(item["date"]),
                payment_method=item["payment_method"],
                installments=item.get("installments", 1),
            )
            for item in unmatched_sales
        ]

        detected = await anomaly_service.detect_all_anomalies(
            tenant_id="tenant-test",
            unmatched_sales=unmatched_sale_entities,
            unmatched_transactions=[],
            matches=[],
        )

        detected_missing = [
            item
            for item in detected
            if item.divergence_type.value == "missing_transaction"
        ]

        recall = (
            len(detected_missing) / len(ground_truth)
            if ground_truth
            else 0.0
        )

        assert recall >= 0.99, f"Missing transaction recall {recall:.4f} < 99% target"
