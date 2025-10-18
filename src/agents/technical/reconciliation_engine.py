"""Reconciliation engine orchestrated by the IA-Developer persona."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple


@dataclass
class ReconciliationResult:
    """Structured response returned after running reconciliation."""

    matched: List[Dict[str, object]]
    unmatched_sales: List[Dict[str, object]]
    unmatched_acquirer: List[Dict[str, object]]
    divergences: List[Dict[str, object]]
    metrics: Dict[str, float]


class ExactMatcher:
    """Performs strict reconciliation based on NSU, amount and date."""

    def match(
        self,
        sales: List[Dict[str, object]],
        transactions: List[Dict[str, object]],
    ) -> Tuple[List[Dict[str, object]], List[Dict[str, object]], List[Dict[str, object]]]:
        matched: List[Dict[str, object]] = []
        remaining_transactions = transactions.copy()
        remaining_sales: List[Dict[str, object]] = []

        for sale in sales:
            match = next(
                (
                    transaction
                    for transaction in remaining_transactions
                    if str(transaction.get("nsu")) == str(sale.get("nsu"))
                    and float(transaction.get("amount", 0.0)) == float(sale.get("amount", 0.0))
                    and str(transaction.get("date")) == str(sale.get("date"))
                ),
                None,
            )
            if match:
                matched.append({"sale": sale, "transaction": match, "confidence": 1.0})
                remaining_transactions.remove(match)
            else:
                remaining_sales.append(sale)

        return matched, remaining_sales, remaining_transactions


class FuzzyMatcher:
    """Performs tolerant matching that allows small monetary discrepancies."""

    def __init__(self, tolerance: float = 0.5) -> None:
        self.tolerance = tolerance

    def match(
        self,
        sales: List[Dict[str, object]],
        transactions: List[Dict[str, object]],
    ) -> Tuple[List[Dict[str, object]], List[Dict[str, object]], List[Dict[str, object]]]:
        matched: List[Dict[str, object]] = []
        remaining_transactions = transactions.copy()
        remaining_sales: List[Dict[str, object]] = []

        for sale in sales:
            match = next(
                (
                    transaction
                    for transaction in remaining_transactions
                    if str(transaction.get("date")) == str(sale.get("date"))
                    and abs(float(transaction.get("amount", 0.0)) - float(sale.get("amount", 0.0)))
                    <= self.tolerance
                ),
                None,
            )
            if match:
                confidence = max(0.85, 1 - abs(float(match.get("amount", 0.0)) - float(sale.get("amount", 0.0))))
                matched.append({"sale": sale, "transaction": match, "confidence": confidence})
                remaining_transactions.remove(match)
            else:
                remaining_sales.append(sale)

        return matched, remaining_sales, remaining_transactions


class MLBasedMatcher:
    """Heuristic based matcher that simulates an ML driven score."""

    def match(
        self,
        sales: List[Dict[str, object]],
        transactions: List[Dict[str, object]],
    ) -> Tuple[List[Dict[str, object]], List[Dict[str, object]], List[Dict[str, object]]]:
        matched: List[Dict[str, object]] = []
        remaining_transactions = transactions.copy()
        remaining_sales = []

        for sale in sales:
            best_match = None
            best_score = 0.0
            for transaction in remaining_transactions:
                amount_diff = abs(float(transaction.get("amount", 0.0)) - float(sale.get("amount", 0.0)))
                score = 1.0 / (1.0 + amount_diff)
                if str(transaction.get("date")) == str(sale.get("date")):
                    score += 0.1
                if score > best_score:
                    best_match = transaction
                    best_score = score
            if best_match is not None:
                matched.append({"sale": sale, "transaction": best_match, "confidence": min(best_score, 0.99)})
                remaining_transactions.remove(best_match)
            else:
                remaining_sales.append(sale)

        return matched, remaining_sales, remaining_transactions


class _BusinessRules:
    """Minimal business rules engine used to prioritise divergences."""

    def calculate_severity(self, divergence: Dict[str, object]) -> str:
        amount = 0.0
        if "sale" in divergence and divergence["sale"]:
            amount = float(divergence["sale"].get("amount", 0.0))
        if amount > 1000:
            return "critical"
        if amount > 100:
            return "high"
        if amount > 10:
            return "medium"
        return "low"

    def suggest_action(self, divergence: Dict[str, object]) -> str:
        if divergence.get("requires_human_review"):
            return "manual_review"
        if divergence.get("type") == "validation_failed":
            return "reprocess"
        return "investigate"


class ReconciliationEngine:
    """Performs multi-stage reconciliation orchestrated by IA-Developer."""

    def __init__(self) -> None:
        self.matching_strategies = [ExactMatcher(), FuzzyMatcher(), MLBasedMatcher()]
        self.business_rules = _BusinessRules()

    async def reconcile(
        self,
        pos_sales: List[Dict[str, object]],
        acquirer_transactions: List[Dict[str, object]],
        context: Dict[str, object],
    ) -> ReconciliationResult:
        matched: List[Dict[str, object]] = []
        divergences: List[Dict[str, object]] = []

        remaining_sales = pos_sales
        remaining_transactions = acquirer_transactions

        matches, remaining_sales, remaining_transactions = self.matching_strategies[0].match(
            remaining_sales,
            remaining_transactions,
        )
        matched.extend(matches)

        if remaining_sales:
            matches, remaining_sales, remaining_transactions = self.matching_strategies[1].match(
                remaining_sales,
                remaining_transactions,
            )
            matched.extend(matches)

        if remaining_sales:
            matches, remaining_sales, remaining_transactions = self.matching_strategies[2].match(
                remaining_sales,
                remaining_transactions,
            )
            for entry in matches:
                if entry.get("confidence", 0.0) > 0.9:
                    matched.append(entry)
                else:
                    entry["requires_human_review"] = True
                    divergences.append(entry)

        for entry in matched:
            if not self.validate_match(entry):
                divergences.append(
                    {
                        "type": "validation_failed",
                        "sale": entry.get("sale"),
                        "transaction": entry.get("transaction"),
                        "issue": self.identify_issue(entry),
                    }
                )

        remaining_unmatched_sales = list(remaining_sales)
        remaining_unmatched_transactions = list(remaining_transactions)

        for divergence in divergences:
            divergence["severity"] = self.business_rules.calculate_severity(divergence)
            divergence["action"] = self.business_rules.suggest_action(divergence)

        total_sales = len(pos_sales) or 1
        metrics = {
            "matching_rate": len(matched) / total_sales,
            "divergence_rate": len(divergences) / total_sales,
        }

        return ReconciliationResult(
            matched=matched,
            unmatched_sales=remaining_unmatched_sales,
            unmatched_acquirer=remaining_unmatched_transactions,
            divergences=divergences,
            metrics=metrics,
        )

    # ------------------------------------------------------------------
    # Validation helpers
    # ------------------------------------------------------------------
    def validate_match(self, match: Dict[str, object]) -> bool:
        sale = match.get("sale", {})
        transaction = match.get("transaction", {})
        if not sale or not transaction:
            return False
        amount_diff = abs(float(transaction.get("amount", 0.0)) - float(sale.get("amount", 0.0)))
        return amount_diff <= 1.0

    def identify_issue(self, match: Dict[str, object]) -> str:
        sale = match.get("sale", {})
        transaction = match.get("transaction", {})
        sale_amount = float(sale.get("amount", 0.0))
        transaction_amount = float(transaction.get("amount", 0.0))
        diff = transaction_amount - sale_amount
        if abs(diff) <= 1.0:
            return "tolerance_exceeded"
        if diff > 0:
            return "acquirer_overcharge"
        return "acquirer_undercharge"

