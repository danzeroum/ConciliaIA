"""Integration specialist agent responsible for ingesting acquirer data."""
from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from typing import Dict, List, Optional

from src.learning.auto_rag import AutoRAG
from src.protocols.ciif import (
    CIIFProtocol,
    HandoffContext,
    HandoffIntention,
    HandoffPackage,
)


class _DefaultParser:
    """Simple parser that normalises transaction payloads."""

    REQUIRED_FIELDS = ("nsu", "amount", "date")

    def parse(self, transaction: Dict[str, object]) -> Dict[str, object]:
        for field in self.REQUIRED_FIELDS:
            if field not in transaction:
                raise ValueError(f"Missing required field '{field}' in transaction")
        normalized = {
            "nsu": str(transaction["nsu"]),
            "amount": float(transaction["amount"]),
            "date": str(transaction["date"]),
            "raw": transaction,
        }
        return normalized


class _MockAcquirerClient:
    """Thin asynchronous client used for bootstrapping the integration pipeline."""

    def __init__(self, name: str) -> None:
        self.name = name

    async def fetch_transactions(
        self,
        start_date: str,
        end_date: str,
        context: Optional[Dict[str, object]] = None,
    ) -> List[Dict[str, object]]:
        await asyncio.sleep(0)
        if context and "seed_transactions" in context:
            return list(context["seed_transactions"])
        return []


class IntegrationSpecialistAgent:
    """Collects, validates and hands off transactions to the developer persona."""

    def __init__(self) -> None:
        self.parsers = self.load_parsers()
        self.api_clients = self.load_api_clients()
        self.ciif = CIIFProtocol()
        self.rag = AutoRAG()
        self.dead_letter: List[Dict[str, object]] = []

    async def collect_transactions(
        self,
        acquirer: str,
        start_date: str,
        end_date: str,
        context: Dict[str, object],
    ) -> HandoffPackage:
        """Collect transactions from the specified acquirer and prepare a CIIF handoff."""

        source = self.select_source(acquirer, context)
        raw_transactions = await self.fetch_from_source(
            acquirer=acquirer,
            source=source,
            start_date=start_date,
            end_date=end_date,
            context=context,
        )

        parser = self.parsers.get(acquirer) or self.parsers["default"]
        normalized_transactions: List[Dict[str, object]] = []
        parse_errors: List[Dict[str, object]] = []

        for transaction in raw_transactions:
            try:
                normalized_transactions.append(parser.parse(transaction))
            except Exception as exc:  # pragma: no cover - defensive
                error = {"raw": transaction, "error": str(exc)}
                parse_errors.append(error)
                self.send_to_dead_letter(error)

        quality_metrics = self.calculate_quality(
            total=len(raw_transactions),
            parsed=len(normalized_transactions),
            errors=len(parse_errors),
        )

        handoff = self.ciif.prepare_handoff(
            from_ia="ia-integration-specialist",
            to_ia="ia-developer",
            artifacts=[
                {
                    "type": "normalized_transactions",
                    "data": normalized_transactions,
                    "schema": {"fields": ["nsu", "amount", "date"]},
                    "quality": quality_metrics,
                },
                {
                    "type": "parse_errors",
                    "data": parse_errors,
                    "requires_manual_review": bool(parse_errors),
                    "metadata": {"constraints": ["manual_review_required"] if parse_errors else []},
                },
            ],
            context=HandoffContext(
                current_stage="data_collection",
                trajectory=["smart_router", "ia-integration-specialist"],
                memory=context.get("memory", {}),
                business_context=f"Coleta {acquirer} para reconciliação",
            ),
            intention=HandoffIntention(
                objective="Reconciliar transações coletadas",
                success_criteria={"matching_rate": 0.995, "processing_time_ms": 100},
                monitoring_metrics=["reconciliation_accuracy", "processing_time"],
                deadline="4 horas",
            ),
        )

        self.rag.index_decision(
            {
                "id": handoff.handoff_id,
                "problem": f"Coletar transações {acquirer}",
                "problem_type": "acquirer_integration",
                "ias_involved": ["ia-integration-specialist"],
                "approach": f"Source: {source}",
                "outcome": "success" if quality_metrics["parse_rate"] > 0.95 else "partial",
                "confidence": quality_metrics["parse_rate"],
                "reasoning": f"Parsed {len(normalized_transactions)}/{len(raw_transactions)}",
                "timestamp": self.now(),
            }
        )

        return handoff

    # ------------------------------------------------------------------
    # Initialisation helpers
    # ------------------------------------------------------------------
    def load_parsers(self) -> Dict[str, _DefaultParser]:
        return {
            "default": _DefaultParser(),
            "Cielo": _DefaultParser(),
            "Rede": _DefaultParser(),
            "Stone": _DefaultParser(),
        }

    def load_api_clients(self) -> Dict[str, _MockAcquirerClient]:
        return {
            "Cielo": _MockAcquirerClient("Cielo"),
            "Rede": _MockAcquirerClient("Rede"),
            "Stone": _MockAcquirerClient("Stone"),
        }

    # ------------------------------------------------------------------
    # Operational helpers
    # ------------------------------------------------------------------
    def select_source(self, acquirer: str, context: Dict[str, object]) -> str:
        preferred = context.get("preferred_source")
        available = context.get("available_sources", ["api", "edi", "manual"])
        if preferred in available:
            return str(preferred)
        if "api" in available and acquirer in self.api_clients:
            return "api"
        if "edi" in available:
            return "edi"
        return "manual"

    async def fetch_from_source(
        self,
        acquirer: str,
        source: str,
        start_date: str,
        end_date: str,
        context: Dict[str, object],
    ) -> List[Dict[str, object]]:
        if source == "api" and acquirer in self.api_clients:
            client = self.api_clients[acquirer]
            return await client.fetch_transactions(start_date=start_date, end_date=end_date, context=context)
        if source == "edi" and context.get("edi_payload"):
            return list(context["edi_payload"])
        if source == "manual" and context.get("manual_input"):
            return list(context["manual_input"])
        return []

    def calculate_quality(self, total: int, parsed: int, errors: int) -> Dict[str, float]:
        if total == 0:
            return {"total": 0, "parsed": parsed, "errors": errors, "parse_rate": 0.0, "error_rate": 0.0}
        return {
            "total": total,
            "parsed": parsed,
            "errors": errors,
            "parse_rate": parsed / total,
            "error_rate": errors / total,
        }

    def send_to_dead_letter(self, payload: Dict[str, object]) -> None:
        payload = dict(payload)
        payload["logged_at"] = self.now()
        self.dead_letter.append(payload)

    @staticmethod
    def now() -> str:
        return datetime.now(timezone.utc).isoformat()

