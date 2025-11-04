import os
from typing import Any, Dict

import pytest
import yaml

WORKFLOW_DIR = ".github/workflows"


def _load_workflow(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}
    if not isinstance(data, dict):
        raise AssertionError(f"Workflow inválido: {os.path.basename(path)}")
    return data


def _has_on_section(data: Dict[str, Any]) -> bool:
    return "on" in data or True in data


@pytest.mark.parametrize(
    "filename",
    [file for file in os.listdir(WORKFLOW_DIR) if file.endswith(".yml")],
)
def test_workflow_has_mandatory_sections(filename):
    path = os.path.join(WORKFLOW_DIR, filename)
    workflow = _load_workflow(path)
    assert "name" in workflow, f"Workflow sem nome: {filename}"
    assert _has_on_section(workflow), f"Workflow sem gatilho: {filename}"
    assert "jobs" in workflow and workflow["jobs"], f"Workflow sem jobs: {filename}"
