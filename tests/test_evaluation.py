import json
from pathlib import Path

from sop_assistant.evaluation import prepare_samples


def test_golden_has_required_categories_and_provenance():
    cases = json.loads(Path("eval/questions.json").read_text(encoding="utf-8"))
    assert len(cases) >= 5
    assert {"answerable", "ambiguous", "unsupported"} <= {c["category"] for c in cases}
    assert all(c["reference"] and c["sources"] for c in cases)
    assert all(s["page"] == 1 and 1 <= s["section"] <= 8 for c in cases for s in c["sources"])


def test_ragas_samples_include_reference_and_real_evidence():
    rows = [
        {
            "case": {"id": "a", "reference": "Reference", "expected_status": "answered"},
            "result": {
                "question": "Question",
                "status": "answered",
                "message": "",
                "statements": [{"text": "Answer", "evidence_ids": ["x"]}],
                "evidence": [{"text": "Actual retrieved context"}],
            },
        }
    ]
    samples = prepare_samples(rows)
    assert samples[0]["response"] == "Answer"
    assert samples[0]["retrieved_contexts"] == ["Actual retrieved context"]
    assert samples[0]["reference"] == "Reference"
