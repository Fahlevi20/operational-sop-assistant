import asyncio
import json
from types import SimpleNamespace

import pytest

from sop_assistant.evaluation import evaluate_samples


class Metric:
    async def ascore(self, **kwargs):
        return SimpleNamespace(value=1.0)


class Rubric:
    async def ascore(self, **kwargs):
        return SimpleNamespace(value="pass", reason="Supported.")


def test_run_records_progress_and_citation_pair_inputs(tmp_path):
    from sop_assistant.eval_metrics import metric_inputs

    sample = {
        "id": "a",
        "expected_status": "answered",
        "status": "answered",
        "user_input": "Q",
        "response": "A",
        "reference": "A",
        "message": "",
        "statements": [{"text": "A", "evidence_ids": ["x", "x"]}],
        "evidence": [{"id": "x", "text": "A", "source": "x.pdf", "page": 1}],
        "citations": [{"id": "x", "source": "x.pdf", "page": 1}],
        "retrieved_contexts": ["A"],
    }
    metrics = {name: Metric() for name in metric_inputs(sample)}
    output = tmp_path / "scores.json"
    asyncio.run(
        evaluate_samples([sample], output, metrics, Rubric(), None, {"input_sha256": "abc"})
    )
    data = json.loads(output.read_text())
    assert data["complete"] is True
    assert data["processed_cases"] == 1
    assert data["provenance"]["input_sha256"] == "abc"
    assert len(data["scores"][0]["citation_pairs"]) == 1
    assert data["scores"][0]["metrics"]["citation_support"]["value"] == 1


def test_existing_output_is_not_overwritten(tmp_path):
    output = tmp_path / "scores.json"
    output.write_text("original")
    with pytest.raises(FileExistsError):
        asyncio.run(evaluate_samples([], output, {}, None, None, {}))
    assert output.read_text() == "original"
