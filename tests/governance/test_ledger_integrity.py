import json
import os

import pytest

LEDGER = ".buildtovalue/ledger/traceability-ledger.jsonl"


@pytest.mark.skipif(not os.path.exists(LEDGER), reason="ledger não gerado ainda")
def test_ledger_entries_have_required_fields():
    with open(LEDGER, "r", encoding="utf-8") as f:
        for line in f:
            entry = json.loads(line)
            for field in ["id", "persona", "task", "outcome", "confidence"]:
                assert field in entry, f"Campo ausente: {field}"
                assert entry[field] not in [None, ""], f"Campo vazio: {field}"
