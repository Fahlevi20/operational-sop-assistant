"""Measure source-page ranking in saved runs without embeddings or model calls."""

import argparse
import hashlib
import json
from pathlib import Path


def measure_ranking(relevant, ranked):
    """Compute page-level recall and first-relevant reciprocal rank."""
    if not relevant:
        raise ValueError("Ranking evaluation needs reference source pages.")
    ranked = list(dict.fromkeys(ranked))
    result = {
        f"recall@{k}": len(relevant.intersection(ranked[:k])) / len(relevant) for k in (1, 2, 4)
    }
    result["mrr"] = next((1 / rank for rank, page in enumerate(ranked, 1) if page in relevant), 0.0)
    return result


def render_rankings(data, digest):
    """Evaluate expected-answerable cases against their saved golden annotations."""
    lines = [
        "# Retrieval Ranking Check",
        "",
        "Offline source-page ranking evaluation of expected-answerable cases only.",
        f"Input SHA256: `{digest}`",
        "",
        "| Case | Recall@1 | Recall@2 | Recall@4 | Reciprocal rank | Retrieved page order |",
        "| --- | ---: | ---: | ---: | ---: | --- |",
    ]
    scores = []
    for row in data["results"]:
        case = row["case"]
        if case["expected_status"] != "answered":
            continue
        relevant = {(s["document"], s["page"]) for s in case["sources"]}
        ranked = [(e["source"], e["page"]) for e in row["result"]["evidence"]]
        result = measure_ranking(relevant, ranked)
        scores.append(result)
        order = " → ".join(f"{name.split('_')[1]} p.{page}" for name, page in dict.fromkeys(ranked))
        cells = [
            case["id"],
            *(f"{result[k]:.3f}" for k in ("recall@1", "recall@2", "recall@4", "mrr")),
            order,
        ]
        lines.append("| " + " | ".join(str(c).replace("|", "\\|") for c in cells) + " |")
    lines.extend(["", "## Summary", "", f"- Cases evaluated: {len(scores)}"])
    for key in ("recall@1", "recall@2", "recall@4", "mrr"):
        mean = f"{sum(s[key] for s in scores) / len(scores):.3f}" if scores else "N/A"
        lines.append(f"- Mean {key}: **{mean}**")
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            (
                "- Recall measures how many annotated required pages appear in the top k; "
                "MRR measures how early the first required page appears."
            ),
            (
                "- Multiple sections on one page count as one relevant page. "
                "This is page-level evaluation, not section-level entailment."
            ),
            (
                "- Reference labels come from the golden case embedded in this saved run. "
                "Incomplete annotations can affect the measurements."
            ),
            (
                "- Returning all four corpus pages guarantees page coverage, not useful ranking. "
                "A cross-document question needs all required pages, not just one relevant hit."
            ),
            (
                "- These are development cases, not a held-out embedding benchmark. "
                "Do not lower retrieval depth based on averages without inspecting every case."
            ),
            "",
        ]
    )
    return "\n".join(lines)


def main():
    """Write a new Markdown report, preserving original run artifacts."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=Path("data/evaluation-english-prompt.json"))
    parser.add_argument("--output", type=Path, default=Path("data/retrieval-ranking.md"))
    args = parser.parse_args()
    raw = args.input.read_bytes()
    report = render_rankings(json.loads(raw), hashlib.sha256(raw).hexdigest())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8") as stream:
        stream.write(report)
    print(f"Saved ranking report to {args.output}")


if __name__ == "__main__":
    main()
