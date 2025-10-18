"""CIIF (Context-Information-Intention-Format) handoff protocol."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, List, Optional
from uuid import uuid4


@dataclass
class HandoffContext:
    """Represents the context portion of the CIIF handoff."""

    current_stage: str
    trajectory: List[str]
    memory: Dict[str, object]
    business_context: str


@dataclass
class HandoffInformation:
    """Payload with the information portion of the handoff."""

    artifacts: List[Dict[str, object]]
    key_decisions: List[Dict[str, object]]
    constraints: List[str]
    known_issues: List[str]


@dataclass
class HandoffIntention:
    """Intent and measurable success criteria."""

    objective: str
    success_criteria: Dict[str, object]
    monitoring_metrics: List[str]
    deadline: str


@dataclass
class HandoffFormat:
    """Desired output format for the receiving persona."""

    output_type: str
    structure: Dict[str, object]
    validation_schema: Dict[str, object]
    quality_gates: List[str]


@dataclass
class HandoffPackage:
    """Top level representation of a CIIF handoff."""

    handoff_id: str
    from_ia: str
    to_ia: str
    timestamp: str
    context: Dict[str, object]
    information: Dict[str, object]
    intention: Dict[str, object]
    format: Dict[str, object]
    quality_assurance: Dict[str, object]


class CIIFProtocol:
    """Context-Information-Intention-Format protocol for orchestrated handoffs."""

    def prepare_handoff(
        self,
        from_ia: str,
        to_ia: str,
        artifacts: List[Dict[str, object]],
        context: HandoffContext,
        intention: HandoffIntention,
        format_override: Optional[HandoffFormat] = None,
    ) -> HandoffPackage:
        """Build a validated handoff package between personas."""

        handoff_id = self.generate_id()
        information_section = {
            "artifacts": artifacts,
            "key_decisions": self.extract_decisions(artifacts),
            "constraints": self.identify_constraints(artifacts),
            "known_issues": self.identify_issues(artifacts),
        }

        format_payload = (
            self.determine_format(to_ia, artifacts)
            if format_override is None
            else self.format_to_dict(format_override)
        )

        package = HandoffPackage(
            handoff_id=handoff_id,
            from_ia=from_ia,
            to_ia=to_ia,
            timestamp=self.now(),
            context={
                "stage": context.current_stage,
                "trajectory": context.trajectory,
                "memory": context.memory,
                "business_context": context.business_context,
            },
            information=information_section,
            intention={
                "objective": intention.objective,
                "success_criteria": intention.success_criteria,
                "monitoring": intention.monitoring_metrics,
                "deadline": intention.deadline,
            },
            format=format_payload,
            quality_assurance={
                "completeness_check": self.check_completeness(artifacts),
                "validation_results": self.validate_artifacts(artifacts),
                "qa_gates": self.get_qa_gates(to_ia),
            },
        )
        return package

    # ------------------------------------------------------------------
    # Helper methods
    # ------------------------------------------------------------------
    @staticmethod
    def generate_id() -> str:
        return str(uuid4())

    @staticmethod
    def now() -> str:
        return datetime.now(timezone.utc).isoformat()

    def extract_decisions(self, artifacts: List[Dict[str, object]]) -> List[Dict[str, object]]:
        decisions: List[Dict[str, object]] = []
        for artifact in artifacts:
            if artifact.get("type", "").endswith("decision"):
                decisions.append({"id": artifact.get("id"), "summary": artifact.get("summary")})
        return decisions

    def identify_constraints(self, artifacts: List[Dict[str, object]]) -> List[str]:
        constraints: List[str] = []
        for artifact in artifacts:
            meta = artifact.get("metadata", {})
            if isinstance(meta, dict):
                constraints.extend(meta.get("constraints", []))
        return constraints

    def identify_issues(self, artifacts: List[Dict[str, object]]) -> List[str]:
        issues: List[str] = []
        for artifact in artifacts:
            problems = artifact.get("known_issues") or artifact.get("issues")
            if isinstance(problems, list):
                issues.extend(str(item) for item in problems)
        return issues

    def determine_format(self, to_ia: str, artifacts: List[Dict[str, object]]) -> Dict[str, object]:
        output_type = "json"
        if any(artifact.get("type") == "normalized_transactions" for artifact in artifacts):
            output_type = "dataframe"
        structure = {"expected_fields": self._collect_fields(artifacts)}
        validation_schema = {"required": structure["expected_fields"]}
        return {
            "output_type": output_type,
            "structure": structure,
            "validation_schema": validation_schema,
            "quality_gates": self.get_qa_gates(to_ia),
        }

    def format_to_dict(self, handoff_format: HandoffFormat) -> Dict[str, object]:
        return {
            "output_type": handoff_format.output_type,
            "structure": handoff_format.structure,
            "validation_schema": handoff_format.validation_schema,
            "quality_gates": handoff_format.quality_gates,
        }

    def check_completeness(self, artifacts: List[Dict[str, object]]) -> Dict[str, float]:
        if not artifacts:
            return {"coverage": 0.0, "has_required": False}
        total = len(artifacts)
        with_data = sum(1 for artifact in artifacts if artifact.get("data"))
        return {"coverage": with_data / total, "has_required": with_data == total}

    def validate_artifacts(self, artifacts: List[Dict[str, object]]) -> Dict[str, object]:
        validations = {}
        for artifact in artifacts:
            name = artifact.get("type", "artifact")
            if artifact.get("data"):
                validations[name] = {"status": "ok", "items": len(artifact.get("data", []))}
            else:
                validations[name] = {"status": "missing", "items": 0}
        return validations

    def get_qa_gates(self, to_ia: str) -> List[str]:
        default_gates = ["schema_validation", "quality_review"]
        if to_ia == "ia-developer":
            return default_gates + ["unit_tests"]
        if to_ia == "ia-qa":
            return default_gates + ["test_plan"]
        return default_gates

    def _collect_fields(self, artifacts: List[Dict[str, object]]) -> List[str]:
        fields: List[str] = []
        for artifact in artifacts:
            schema = artifact.get("schema")
            if isinstance(schema, dict):
                fields.extend(schema.get("fields", []))
        return sorted(set(fields))

