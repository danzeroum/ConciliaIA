"""Synthetic dataset generator for reconciliation accuracy validation."""

from __future__ import annotations

import json
import random
from dataclasses import asdict, dataclass
from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from typing import Dict, List

DATASET_DIR = Path(__file__).resolve().parent
RANDOM_SEED = 42


@dataclass
class SaleRecord:
    """Serializable representation of a sale used for testing."""

    id: str
    tenant_id: str
    nsu: str
    amount: float
    date: str
    payment_method: str
    installments: int
    installment_number: int | None = None


@dataclass
class TransactionRecord:
    """Serializable representation of an acquirer transaction."""

    id: str
    tenant_id: str
    acquirer: str
    nsu: str
    transaction_date: str
    settlement_date: str
    gross_amount: float
    mdr_fee: float
    net_amount: float
    installments: int
    installment_number: int | None = None


def _to_float(value: Decimal) -> float:
    return float(value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def _generate_exact_matches(start_index: int, total: int) -> Dict[str, List[dict]]:
    sales: List[dict] = []
    transactions: List[dict] = []
    ground_truth: List[dict] = []

    for index in range(total):
        current = start_index + index
        nsu = f"NSU{current:08d}"
        amount = Decimal(random.randint(5_000, 50_000)) / Decimal("100")
        sale_date = date(2025, 1, random.randint(1, 28))

        sale = SaleRecord(
            id=f"sale-{current}",
            tenant_id="tenant-test",
            nsu=nsu,
            amount=_to_float(amount),
            date=sale_date.isoformat(),
            payment_method=random.choice(["debit", "credit_1x"]),
            installments=1,
        )

        transaction = TransactionRecord(
            id=f"txn-{current}",
            tenant_id="tenant-test",
            acquirer=random.choice(["cielo", "rede"]),
            nsu=nsu,
            transaction_date=sale_date.isoformat(),
            settlement_date=(sale_date + timedelta(days=30)).isoformat(),
            gross_amount=_to_float(amount),
            mdr_fee=_to_float(amount * Decimal("0.03")),
            net_amount=_to_float(amount * Decimal("0.97")),
            installments=1,
        )

        sales.append(asdict(sale))
        transactions.append(asdict(transaction))
        ground_truth.append(
            {
                "sale_id": sale.id,
                "transaction_id": transaction.id,
                "match_type": "exact",
                "expected_confidence": 1.0,
            }
        )

    return {
        "sales": sales,
        "transactions": transactions,
        "ground_truth_matches": ground_truth,
    }


def _generate_fuzzy_matches(start_index: int, total: int) -> Dict[str, List[dict]]:
    sales: List[dict] = []
    transactions: List[dict] = []
    ground_truth: List[dict] = []

    for index in range(total):
        current = start_index + index
        nsu = f"NSU{current:08d}"
        base_amount = Decimal(random.randint(10_000, 50_000)) / Decimal("100")
        variance = Decimal(random.randint(-50, 50)) / Decimal("100")
        sale_amount = base_amount
        transaction_amount = base_amount + variance
        sale_date = date(2025, 1, random.randint(1, 28))

        sale = SaleRecord(
            id=f"sale-{current}",
            tenant_id="tenant-test",
            nsu=nsu,
            amount=_to_float(sale_amount),
            date=sale_date.isoformat(),
            payment_method="credit_1x",
            installments=1,
        )

        transaction = TransactionRecord(
            id=f"txn-{current}",
            tenant_id="tenant-test",
            acquirer="cielo",
            nsu=nsu,
            transaction_date=sale_date.isoformat(),
            settlement_date=(sale_date + timedelta(days=30)).isoformat(),
            gross_amount=_to_float(transaction_amount),
            mdr_fee=_to_float(transaction_amount * Decimal("0.03")),
            net_amount=_to_float(transaction_amount * Decimal("0.97")),
            installments=1,
        )

        sales.append(asdict(sale))
        transactions.append(asdict(transaction))

        if abs(variance) <= Decimal("0.50"):
            ground_truth.append(
                {
                    "sale_id": sale.id,
                    "transaction_id": transaction.id,
                    "match_type": "fuzzy_amount",
                    "expected_confidence": 0.9,
                }
            )

    return {
        "sales": sales,
        "transactions": transactions,
        "ground_truth_matches": ground_truth,
    }


def _generate_installments(start_index: int, total: int) -> Dict[str, List[dict]]:
    sales: List[dict] = []
    transactions: List[dict] = []
    ground_truth: List[dict] = []

    for index in range(total):
        current = start_index + index
        base_nsu = f"NSU{current:08d}"
        total_amount = Decimal(random.randint(30_000, 100_000)) / Decimal("100")
        installments = random.choice([3, 6, 12])
        installment_amount = (total_amount / installments).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )

        for inst_number in range(1, installments + 1):
            sale = SaleRecord(
                id=f"sale-{current}-inst{inst_number}",
                tenant_id="tenant-test",
                nsu=f"{base_nsu}-{inst_number}",
                amount=_to_float(installment_amount),
                date=date(2025, 1, 15).isoformat(),
                payment_method=f"credit_{installments}x",
                installments=installments,
                installment_number=inst_number,
            )

            transaction = TransactionRecord(
                id=f"txn-{current}-inst{inst_number}",
                tenant_id="tenant-test",
                acquirer="cielo",
                nsu=f"{base_nsu}-{inst_number}",
                transaction_date=date(2025, 1, 15).isoformat(),
                settlement_date=(date(2025, 1, 15) + timedelta(days=30 * inst_number)).isoformat(),
                gross_amount=_to_float(installment_amount),
                mdr_fee=_to_float(installment_amount * Decimal("0.035")),
                net_amount=_to_float(installment_amount * Decimal("0.965")),
                installments=installments,
                installment_number=inst_number,
            )

            sales.append(asdict(sale))
            transactions.append(asdict(transaction))
            ground_truth.append(
                {
                    "sale_id": sale.id,
                    "transaction_id": transaction.id,
                    "match_type": "installment",
                    "expected_confidence": 0.98,
                }
            )

    return {
        "sales": sales,
        "transactions": transactions,
        "ground_truth_matches": ground_truth,
    }


def _generate_missing_transactions(start_index: int, total: int) -> Dict[str, List[dict]]:
    sales: List[dict] = []
    ground_truth: List[dict] = []

    for index in range(total):
        current = start_index + index
        nsu = f"NSU{current:08d}"
        amount = Decimal(random.randint(10_000, 200_000)) / Decimal("100")
        days_old = random.choice([8, 35, 95])
        sale_date = date.today() - timedelta(days=days_old)

        sale = SaleRecord(
            id=f"sale-{current}",
            tenant_id="tenant-test",
            nsu=nsu,
            amount=_to_float(amount),
            date=sale_date.isoformat(),
            payment_method="credit_1x",
            installments=1,
        )

        sales.append(asdict(sale))

        severity = "medium" if days_old <= 30 else ("high" if days_old <= 90 else "critical")
        ground_truth.append(
            {
                "sale_id": sale.id,
                "type": "missing_transaction",
                "severity": severity,
                "amount_at_risk": _to_float(amount),
            }
        )

    return {
        "sales": sales,
        "ground_truth_divergences": ground_truth,
    }


def generate_test_dataset(n_transactions: int = 10_000) -> Dict[str, List[dict]]:
    """Generate a dataset with deterministic random data."""

    random.seed(RANDOM_SEED + n_transactions)

    dataset = {
        "sales": [],
        "transactions": [],
        "ground_truth_matches": [],
        "ground_truth_divergences": [],
    }

    exact_total = int(n_transactions * 0.70)
    fuzzy_total = int(n_transactions * 0.20)
    installments_total = int(n_transactions * 0.05)
    anomalies_total = n_transactions - (exact_total + fuzzy_total + installments_total)

    segments = [
        _generate_exact_matches(0, exact_total),
        _generate_fuzzy_matches(exact_total, fuzzy_total),
        _generate_installments(exact_total + fuzzy_total, installments_total),
        _generate_missing_transactions(
            exact_total + fuzzy_total + installments_total, anomalies_total
        ),
    ]

    for segment in segments:
        dataset["sales"].extend(segment.get("sales", []))
        dataset["transactions"].extend(segment.get("transactions", []))
        dataset["ground_truth_matches"].extend(segment.get("ground_truth_matches", []))
        dataset["ground_truth_divergences"].extend(
            segment.get("ground_truth_divergences", [])
        )

    return dataset


def save_dataset(dataset: Dict[str, List[dict]], filename: str) -> Path:
    """Persist dataset to disk and return the file path."""

    target_path = DATASET_DIR / filename
    target_path.parent.mkdir(parents=True, exist_ok=True)
    with target_path.open("w", encoding="utf-8") as handler:
        json.dump(dataset, handler, indent=2)
    return target_path


def generate_and_save_default_datasets() -> None:
    for size in (1_000, 10_000, 50_000):
        dataset = generate_test_dataset(size)
        path = save_dataset(dataset, f"test_dataset_{size}.json")
        print(
            f"✅ Dataset generated: {path.name} | "
            f"Sales: {len(dataset['sales'])} | Transactions: {len(dataset['transactions'])}"
        )


if __name__ == "__main__":
    generate_and_save_default_datasets()
