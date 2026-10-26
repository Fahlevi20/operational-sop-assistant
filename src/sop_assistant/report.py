"""Convert saved Ragas scores to readable Markdown without model calls."""

import argparse
import json
from pathlib import Path


def _cell(value):
    return str(value).replace("|", "\\|").replace("\r", " ").replace("\n", " ")


def render_report(data):
    """Summarize this project's Ragas JSON; unscored cases stay unscored."""
    if not isinstance(data.get("scores"), list):
        raise ValueError("Expected a Ragas result containing a scores list.")  # noqa: TRY004
    if data.get("schema_version") == 2:
        return _comprehensive(data)
    rows = data["scores"]
    values = [row["faithfulness"] for row in rows if row.get("faithfulness") is not None]
    average = f"{sum(values) / len(values):.3f}" if values else "N/A"
    matches = sum(row.get("status_matches") is True for row in rows)
    lines = [
        "# Ragas Evaluation Report",
        "",
        "## Summary",
        "",
        f"- Cases recorded: **{len(rows)}**",
        f"- Expected-status matches: **{matches}/{len(rows)}**",
        f"- Cases scored for faithfulness: **{len(values)}/{len(rows)}**",
        f"- Mean faithfulness (scored cases only): **{average}**",
        "",
        "## Per-case results",
        "",
        "| Case | Expected status matched | Faithfulness | Notes |",
        "| --- | --- | --- | --- |",
    ]
    for row in rows:
        score = row.get("faithfulness")
        score_text = "Not scored" if score is None else f"{score:.3f}"
        matched = {True: "Yes", False: "No"}.get(row.get("status_matches"), "Unknown")
        cells = [row["id"], matched, score_text, row.get("note", "—")]
        lines.append("| " + " | ".join(_cell(cell) for cell in cells) + " |")
    lines.extend(
        [
            "",
            "## Interpretation and limitations",
            "",
            (
                "- Faithfulness measures whether the judge considers claims supported "
                "by retrieved context; "
                "it is not a correctness or completeness guarantee."
            ),
            (
                "- Expected-status agreement checks "
                "answered/unsupported/clarification classification, "
                "not the factual accuracy of the answer."
            ),
            (
                "- Not-scored cases are excluded from the mean, not counted as zero. "
                "Review unsupported and clarification responses manually."
            ),
            (
                "- These scores describe only the saved run. "
                "Changing the prompt or answers requires "
                "a new evaluation; conversion does not rerun Ragas."
            ),
            "",
        ]
    )
    return "\n".join(lines)


METRIC_DESCRIPTIONS = {
    "faithfulness": "Support for factual statements in the retrieved context (all statuses).",
    "factual_correctness": "F1 agreement with the reference: supported facts and omissions.",
    "context_precision": "Whether relevant retrieved passages rank early.",
    "context_recall": "Coverage of reference facts by retrieved evidence.",
    "response_relevancy": "Question–answer alignment; not a truth score.",
    "citation_coverage": "Fraction of statements with nonempty, resolvable citation IDs.",
    "citation_validity": "Fraction of referenced IDs that exist in retrieved evidence.",
    "citation_metadata": "Resolved citation source/page matches trusted evidence.",
    "citation_support": "Judge support for statement–cited-passage pairs.",
    "message_contract": "No uncited SOP facts in the free-text message (custom rubric).",
    "decision_quality": "Appropriate answer, abstention or clarification (custom rubric).",
}


# pylint: disable-next=too-many-locals
def _comprehensive(data):
    rows = data["scores"]
    matches = sum(row.get("status_matches") is True for row in rows)
    provenance = data.get("provenance", {})
    lines = [
        "# Comprehensive RAG Evaluation",
        "",
        "## Bottom line",
        "",
        (
            f"- Run: **{'Complete' if data.get('complete') else 'Incomplete'}**; "
            f"processed {data.get('processed_cases', 0)}/{data.get('expected_cases', 0)} cases."
        ),
        f"- Expected-status matches: **{matches}/{len(rows)}**.",
        "- This is not a production readiness certificate or a universal accuracy score.",
        (
            "- If retrieval returns the entire corpus, high recall does not "
            "demonstrate selective retrieval quality."
        ),
        "",
        "### Findings requiring review",
        "",
    ]
    findings = 0
    for row in rows:
        for name, metric in row.get("metrics", {}).items():
            value = metric.get("value")
            if metric["status"] in {"error", "uncertain"} or (
                metric["status"] == "scored" and value is not None and value < 1 - 1e-8
            ):
                findings += 1
                lines.append(
                    f"- **{_cell(row['id'])} / {name}**: "
                    f"{metric['status']}, {value}; {_cell(metric.get('reason', ''))}"
                )
    if not findings:
        lines.append(
            "- No sub-maximum scores or measurement errors recorded. "
            "Skipped metrics and judge limitations still require review."
        )
    lines.extend(
        [
            "",
            "## Metric summary",
            "",
            "Higher is better for numeric scores; denominators differ by applicability.",
            "",
            "| Metric | Mean | Scored | Skipped | Error/uncertain | Meaning |",
            "| --- | ---: | ---: | ---: | ---: | --- |",
        ]
    )
    for name, description in METRIC_DESCRIPTIONS.items():
        metrics = [r.get("metrics", {}).get(name, {"status": "pending"}) for r in rows]
        values = [
            m["value"]
            for m in metrics
            if m["status"] == "scored" and isinstance(m.get("value"), (int, float))
        ]
        mean = f"{sum(values) / len(values):.3f}" if values else "N/A"
        skipped = sum(m["status"] == "skipped" for m in metrics)
        errors = sum(m["status"] in {"error", "uncertain"} for m in metrics)
        lines.append(
            f"| {name} | {mean} | {len(values)}/{len(rows)} | {skipped} | "
            f"{errors} | {description} |"
        )
    lines.extend(["", "## Run provenance", ""])
    lines.extend(f"- **{_cell(key)}**: {_cell(value)}" for key, value in provenance.items())
    lines.extend(["", "## Per-case answers and evaluation", ""])
    for row in rows:
        sample = row.get("sample", {})
        lines.extend(
            [
                f"### {_cell(row['id'])}",
                "",
                f"**Question:** {_cell(sample.get('user_input', 'Not recorded'))}",
                "",
                (
                    f"**Status:** {sample.get('status', 'Unknown')} "
                    f"(expected: {sample.get('expected_status', 'Unknown')})"
                ),
                "",
                "**Answer:**",
                "",
            ]
        )
        evidence = {e["id"]: e for e in sample.get("evidence", [])}
        for statement in sample.get("statements", []):
            citations = []
            for identity in statement["evidence_ids"]:
                item = evidence.get(identity, {})
                citations.append(f"{item.get('source', identity)}, page {item.get('page', '?')}")
            lines.append(f"- {_cell(statement['text'])} **[{'; '.join(map(_cell, citations))}]**")
        if sample.get("message"):
            lines.extend(["", _cell(sample["message"])])
        lines.extend(
            [
                "",
                f"**Reference:** {_cell(sample.get('reference', 'Unknown'))}",
                "",
                "| Metric | Score/verdict | Explanation |",
                "| --- | --- | --- |",
            ]
        )
        for name, metric in row.get("metrics", {}).items():
            result = metric.get("verdict", metric.get("value"))
            lines.append(
                f"| {name} | {_cell(result)} ({metric['status']}) | "
                f"{_cell(metric.get('reason', ''))} |"
            )
        for pair in row.get("citation_pairs", []):
            lines.append(
                f"- Citation check, statement {pair['statement']}, "
                f"`{_cell(pair['id'])}`: {pair.get('verdict', pair['status'])}. "
                f"{_cell(pair.get('reason', ''))}"
            )
        lines.append("")
    lines.extend(
        [
            "## How to draw a conclusion",
            "",
            "- Low context recall: review missing evidence before changing the answer prompt.",
            "- Low correctness with good grounding: inspect missing reference facts or exceptions.",
            (
                "- Low citation support: inspect the actual cited passage, "
                "not just retrieval as a whole."
            ),
            "- Decision/message failures: review abstention, clarification and uncited claims.",
            "- Errors or uncertain judgments: fix or manually review them; do not count as zero.",
            (
                "- A small development set and a model judge do not establish generalization. "
                "Validate references and calibrate judgments with human review."
            ),
            "",
        ]
    )
    return "\n".join(lines)


def main():
    """Read an existing score file and create a new Markdown report."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=Path("data/ragas.json"))
    parser.add_argument("--output", type=Path, default=Path("data/ragas-report.md"))
    args = parser.parse_args()
    try:
        report = render_report(json.loads(args.input.read_text(encoding="utf-8")))
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("x", encoding="utf-8") as stream:
            stream.write(report)
    except (OSError, ValueError, KeyError, TypeError) as error:
        parser.exit(1, f"Report conversion failed: {error}\n")
    print(f"Saved Markdown report to {args.output}")


if __name__ == "__main__":
    main()
