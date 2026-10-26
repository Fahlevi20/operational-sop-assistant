# Evaluation record

## Verified locally — 26 October 2026

- `uv run pytest -q`: **23 passed** at the latest completed run.
- `uv run ruff check src tests`: passed.
- `uv run pylint src/sop_assistant`: **10.00/10**, no reported findings at that run.
- `uv run sop extract`: all four documents produced nonempty text with original page 1 provenance.

| SOP | Method | Extracted characters |
|---|---|---:|
| KB01 ticket handling | Windows OCR | 1,688 |
| KB02 complaint handling | Native | 1,860 |
| KB03 operations | Native, column-aware | 1,686 |
| KB04 escalation/incidents | Windows OCR | 1,771 |

The extraction text was inspected. KB03 sections 7 and 8 follow sections 1–6, including temporary ticket recording with original receipt time and subsequent backfill. Raw scan OCR has `Pl`/`SEVI` identifier substitutions. These are documented rather than silently corrected.

## Golden cases

Ten cases in `eval/questions.json` cover initial response versus resolution, P1 ticket closure exceptions, recurring complaints, ticket-system outage handling, customer versus internal update intervals, an ambiguous update request, sensitive-data escalation outside service hours, and unsupported compensation amounts, resolution SLAs, and retention periods.

Reference answers and supporting sections were authored from the supplied SOPs and inspected extraction. Before submission, verify references visually against the original scans, especially OCR identifiers. The same set is used for development: results are not held-out generalization estimates.

## Live evaluation status

**Not run yet.** No OpenAI API key was configured when checked. Therefore no real answer quality, retrieval hit rate, token cost, latency, or Ragas faithfulness score is claimed. Offline tests cannot establish live model quality.

Next steps after configuring `.env`:
1. Run `uv run sop ingest`, then repeat it to verify the unchanged-corpus no-op.
2. Run `uv run sop evaluate` to capture actual outputs.
3. Run `uv run --group eval python -m sop_assistant.evaluation` for additional Ragas judge calls.
4. Manually compare each answer against its reference and original sources. Record errors and actual fixes here.

Ragas Faithfulness scores answered cases against retrieved contexts; it is not a gold-answer accuracy score. Unsupported and clarification cases need manual review; expected-status agreement alone is insufficient. The judge and generator may share a model family, creating correlated evaluation bias.

## Improvement priorities

1. Complete live evaluation and address observed retrieval/grounding failures before polishing UI.
2. Add portable Indonesian OCR and regression tests against reviewed page transcriptions.
3. Improve extraction diagnostics for nonempty but corrupted text layers and complex layouts.
4. Measure section-level retrieval recall and add reranking only if observed misses justify it.
5. Expand a held-out evaluation set and use independent human review for policy-sensitive answers.

## Reproducibility boundary

Dependencies are locked with uv. The local environment was installed and commands exercised, but an independent clean-machine install and live API workflow have not yet been verified. Windows OCR availability remains a platform prerequisite. Supplied PDFs are excluded from Git pending redistribution permission.
