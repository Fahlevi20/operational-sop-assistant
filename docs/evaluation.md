# Evaluation record

## Scope and interpretation

The ten human-authored Indonesian cases in `eval/questions.json` are a development set, not a held-out production benchmark. They cover response versus resolution, closure exceptions, recurring complaints, ticket-system outages, internal versus customer updates, ambiguous requests, security escalation and unsupported amounts/deadlines/retention periods.

The current corpus contains four one-page SOPs. Whole-page chunks preserve rules and exceptions, and all four pages are retrieved for each test question. High retrieval coverage on this corpus does not demonstrate selective retrieval at scale.

## Saved runs

- `data/evaluation.json`: earlier whole-page generation run.
- `data/ragas.json`: historical Faithfulness-only evaluation: six answered cases scored 1.000, ten expected statuses matched. These scores do **not** evaluate the later prompt change.
- `data/evaluation-english-prompt.json`: revised English system prompt, Indonesian responses. Ten expected statuses matched; inspected refund policy statements carry KB02/page 1 citations rather than uncited message details.
- `data/ragas-comprehensive.json`: expanded evaluation of the explicitly selected saved answers. Check `complete`, processed counts, source SHA256 and per-metric states before drawing conclusions.

Artifacts under `data/` are local and ignored by Git.

### Expanded live result — 26 October 2026

The expanded run completed all ten cases with no metric errors or uncertain aggregate judgments. Expected-status agreement was 10/10. Per-case macro means (not one combined score):

| Metric | Mean | Scored cases |
| --- | ---: | ---: |
| Faithfulness, statements only | 0.983 | 10 |
| Factual Correctness F1 | 0.800 | 6 |
| Context Precision | 0.606 | 6 |
| Context Recall | 1.000 | 6 |
| Response Relevancy | 0.811 | 6 |
| Citation coverage / validity / metadata | 1.000 each | 10 |
| Citation support, mean of each case's pair support | 0.910 | 10 |
| Message contract / decision rubric | 1.000 each | 10 |

Interpretation: evidence coverage is high, but reference agreement and citation entailment need review. The closure judge flagged a general two-day closure statement without its P1 exception in that same statement. The update-cadences judge flagged a combined P1/SEV1 distinction cited to two passages that individually support only part of it. This is a deliberately strict per-citation-passage check: read the full answer and joint evidence before concluding the policy itself is wrong. Security Faithfulness was 0.833. Automated findings are review candidates, not independently verified errors.

The prompt's uncited-message issue did not recur in these ten evaluated outputs. This observation does not close the code-level enforcement gap. Full questions, cited answers, references, pair verdicts and per-case metrics are available through the Markdown converter.

## Follow-up review and ranking check — 26 October 2026

The four flagged answers (closure, recurring complaints, update cadences, security after hours) were compared with the full original PDF pages, including visual inspection of scans. No substantive policy error was identified in those four full answers. This is a targeted review, not a guarantee for other or future answers.

- **Closure:** the full answer includes the P1 exception, but the isolated general statement was penalized for omitting it. The reference also omits the valid customer-confirmed resolution closure route. Keeping rules/exceptions together would improve clarity.
- **Recurring complaints:** the answer preserves the same-issue/30-day condition from KB02 section 6. The shorter reference omits that qualification. The precise correctness deduction is unknown because no detailed verdict was saved.
- **Update cadences:** both timings and audiences match KB03 section 4 and KB04 section 5. The classification comparison combines two sources, so the each-passage-must-support-every-part rubric penalizes valid joint evidence. Its Context Precision score of zero is questionable: the two annotated required pages rank first and second.
- **Security:** the answer's claims match KB04 sections 2, 3 and 6. The Faithfulness deduction is unexplained; OCR substitutions and judge variability are possible factors, not verified causes.

Do not replace historical scores with manually improved numbers. Future evaluation should expand abbreviated references, distinguish joint citation sufficiency from individual citation relevance, and retain claim-level judge verdicts where available.

An offline page-ranking check reused the same saved run and embedded golden source annotations, excluding unsupported/clarification cases. Six expected-answerable cases yielded Recall@1 **0.583**, Recall@2 **0.833**, Recall@4 **1.000**, and MRR **0.806**. Multiple annotated sections on one page count once. The security escalation page ranks third, so top-2 retrieval would omit required evidence. Keeping all four short pages is therefore a measured coverage trade-off, not evidence of strong selective retrieval. See [ranking details](retrieval-ranking.md).

Reproduce without model calls:

```powershell
uv run python -m sop_assistant.retrieval_report --input data/evaluation-english-prompt.json --output data/retrieval-ranking-new.md
```

The source run under `data/` is not bundled; the published Markdown preserves its SHA256 and observed rankings. To inspect rankings for a new run, provide that run's JSON instead.

## Comprehensive metrics

| Metric | Purpose | Applicability |
| --- | --- | --- |
| Faithfulness | Support for generated factual statements in retrieved evidence | Factual statements in all response statuses |
| Factual Correctness F1 | Agreement with reference facts, including omissions | Expected-answerable cases |
| Context Precision | Relevant retrieved evidence ranks early | Expected-answerable cases |
| Context Recall | Retrieved evidence covers reference claims | Expected-answerable cases |
| Response Relevancy | Question/answer alignment, using local EmbeddingGemma | Substantive answered cases |
| Citation coverage/validity/metadata | Structural citation attachment and trusted source/page consistency | Statements/citations present |
| Citation support | Custom judge checks each statement against each cited passage | Cited statements in all statuses |
| Message contract | Custom rubric checks for uncited SOP facts in message | All cases |
| Decision quality | Custom rubric checks answer, abstention or clarification behavior | All cases, including false abstention |

Custom checks are not official Ragas metrics. Citation coverage does not prove entailment. Faithfulness does not prove completeness. F1 depends on the reference quality. Response relevancy is not factual correctness. Model judges can be wrong and may share biases with the answering model.

Unscored, uncertain, failed and pending measurements are not zero and must not be hidden in an average. Each metric has its own denominator; there is no combined overall score or production pass threshold.

## Commands

```powershell
uv run pytest -q
uv run ruff check src tests
uv run pylint src/sop_assistant
# Additional hosted judge calls; keep API keys only in ignored .env.
uv run --group eval python -m sop_assistant.evaluation --input data/evaluation-english-prompt.json --output data/ragas-comprehensive.json
# Offline Markdown conversion; choose unused destination paths on repeat runs.
uv run python -m sop_assistant.report --input data/ragas-comprehensive.json --output data/ragas-comprehensive.md
```

Judge model uses `JUDGE_MODEL`, falling back to the selected provider's model setting. No OmniRoute server settings are changed. Local evaluation embeddings use the existing downloaded model. Checkpointed JSON preserves partial progress and metric errors. Existing result/report files are not overwritten.

## Extraction and remaining limitations

All four supplied PDFs produced nonempty page-1 text. KB01/KB04 required Windows OCR; KB02/KB03 used native extraction with column-aware ordering. Observed character counts were 1,688 / 1,860 / 1,686 / 1,771 respectively. Raw OCR has `Pl`/`SEVI` substitutions; source evidence is not silently rewritten. References should be visually verified against scans before policy-sensitive use.

Structural answer validation checks existing citation IDs but does not semantically enforce the free-text message contract. The revised prompt improved the observed refund response; the evaluator detects violations rather than guaranteeing future model compliance.

Production follow-up: calibrate rubric judgments against independent human review, add held-out and adversarial cases, test retrieval with distractor documents, and monitor latency/errors/cost alongside quality. A clean-machine install and production deployment have not been verified.
