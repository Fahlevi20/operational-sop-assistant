"""Metric applicability and deterministic checks; no optional imports or API calls."""

import math


def outcome(value=None, status="scored", reason=""):
    """Represent unavailable measurements explicitly rather than as zeros."""
    return {"status": status, "value": value, "reason": reason}


def metric_inputs(sample):
    """Keep retrieval evaluation independent of the generator's status decision."""
    question = sample["user_input"]
    contexts = sample["retrieved_contexts"]
    facts = "\n".join(s["text"] for s in sample["statements"] if s["text"].strip())
    answerable = sample["expected_status"] == "answered"
    retrieval = {
        "user_input": question,
        "reference": sample["reference"],
        "retrieved_contexts": contexts,
    }
    return {
        "faithfulness": {"user_input": question, "response": facts, "retrieved_contexts": contexts}
        if facts and contexts
        else None,
        "factual_correctness": {"response": sample["response"], "reference": sample["reference"]}
        if answerable and sample["response"].strip()
        else None,
        "context_precision": retrieval if answerable and contexts else None,
        "context_recall": retrieval if answerable else None,
        "response_relevancy": {"user_input": question, "response": sample["response"]}
        if answerable and sample["status"] == "answered" and facts
        else None,
    }


async def score_metric(metric, inputs):
    """Isolate judge failures and reject nonfinite scores without leaking errors."""
    if inputs is None:
        return outcome(status="skipped", reason="Not applicable or required factual input absent.")
    if inputs.get("retrieved_contexts") == [] and "reference" in inputs:
        return outcome(0.0, reason="No retrieved evidence covers the reference facts.")
    try:
        result = await metric.ascore(**inputs)
        value = float(result.value)
        if not math.isfinite(value):
            return outcome(status="error", reason="Judge returned a nonfinite score.")
        return outcome(value)
    # pylint: disable-next=broad-exception-caught
    except Exception as error:  # noqa: BLE001 -- isolate external judge failures
        return outcome(status="error", reason=f"Metric failed ({type(error).__name__}).")


def citation_structure(sample):
    """Measure structural coverage, validity and trusted source/page consistency."""
    known = {e["id"]: e for e in sample["evidence"]}
    statements = [s for s in sample["statements"] if s["text"].strip()]
    ids = [i for s in statements for i in set(s["evidence_ids"])]
    covered = sum(
        bool(s["evidence_ids"]) and all(i in known for i in s["evidence_ids"]) for s in statements
    )
    metadata = sample.get("citations", [])
    consistent = all(
        c["id"] in known and all(c.get(k) == known[c["id"]].get(k) for k in ("source", "page"))
        for c in metadata
    )
    consistent = consistent and set(ids) == {c["id"] for c in metadata}
    return {
        "coverage": outcome(covered / len(statements))
        if statements
        else outcome(status="skipped", reason="No factual statements."),
        "validity": outcome(sum(i in known for i in ids) / len(ids))
        if ids
        else outcome(status="skipped", reason="No citation IDs."),
        "metadata": outcome(float(consistent))
        if ids or metadata
        else outcome(status="skipped", reason="No citation metadata."),
    }
