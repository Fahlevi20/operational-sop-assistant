import asyncio
import math
from types import SimpleNamespace

from sop_assistant.eval_metrics import citation_structure, metric_inputs, score_metric


def sample():
    return {
        "expected_status": "unsupported",
        "status": "unsupported",
        "user_input": "Amount?",
        "reference": "Not specified",
        "response": "Approval required. Not specified.",
        "statements": [{"text": "Approval required.", "evidence_ids": ["a"]}],
        "message": "Not specified.",
        "retrieved_contexts": ["Approval required."],
        "evidence": [{"id": "a", "source": "a.pdf", "page": 1, "text": "Approval required."}],
        "citations": [{"id": "a", "source": "a.pdf", "page": 1}],
    }


def test_grounding_includes_facts_in_unsupported_answers():
    inputs = metric_inputs(sample())
    assert inputs["faithfulness"]["response"] == "Approval required."
    assert inputs["context_recall"] is None
    assert inputs["factual_correctness"] is None
    assert inputs["response_relevancy"] is None


def test_false_abstention_does_not_skip_retrieval_metrics():
    row = sample()
    row["expected_status"] = "answered"
    assert metric_inputs(row)["context_recall"] is not None


def test_citation_structure_and_empty_denominators():
    row = sample()
    result = citation_structure(row)
    assert result["coverage"]["value"] == 1
    assert result["validity"]["value"] == 1
    row["statements"][0]["evidence_ids"] = ["invented"]
    assert citation_structure(row)["coverage"]["value"] == 0
    row["statements"] = []
    assert citation_structure(row)["coverage"]["status"] == "skipped"


def test_metric_errors_and_nan_are_not_scores():
    class Metric:
        async def ascore(self, **kwargs):
            return SimpleNamespace(value=math.nan)

    result = asyncio.run(score_metric(Metric(), {"response": "x"}))
    assert result["status"] == "error"
    assert result["value"] is None


def test_empty_retrieval_on_answerable_case_counts_as_zero_recall():
    row = sample()
    row["expected_status"] = "answered"
    row["retrieved_contexts"] = []
    result = asyncio.run(score_metric(None, metric_inputs(row)["context_recall"]))
    assert result["status"] == "scored"
    assert result["value"] == 0


def test_skipped_metric_does_not_call_judge():
    assert asyncio.run(score_metric(None, None))["status"] == "skipped"
