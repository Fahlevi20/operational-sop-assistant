# Operational SOP Assistant

A Python/Qdrant proof of concept for answering Indonesian operational SOP questions with document/page citations, clarification for ambiguous requests, and honest handling of missing information.

**Start with the results:** [readable demonstration and metric report](docs/ragas-comprehensive-report.md) · [evaluation notes and limitations](docs/evaluation.md).

## What runs where

- **Local:** PDF extraction, conditional Windows OCR, CPU `google/embeddinggemma-300m` embeddings (768 dimensions), and persistent Qdrant local mode.
- **LLM endpoint:** an authorized OpenAI-compatible service generates answers and optionally judges evaluation results. The tested setup used a user-managed OmniRoute endpoint and route `cx/gpt-5.6-luna-low`. This route name is provider-specific; it is not a guarantee of the underlying model identity or availability.
- **Not required:** Docker, GPU, web UI, deployment, or a paid embedding API.

This is a recruitment proof of concept, not a production service. HR approved a public repository. The supplied PDFs are not bundled; reviewers must provide their copies.

## Quick start — PowerShell

Tested on Windows 11 with Python 3.13. Requirements: Python 3.11+, [uv](https://docs.astral.sh/uv/), enough disk/RAM for the local embedding model, a Windows OCR language pack, and access to a compatible LLM endpoint. Image-only PDFs currently require Windows OCR.

1. Place the four SOP PDFs in `Knowledge Base/`. Do **not** place the assignment brief there.
2. Install dependencies and create your local configuration:

```powershell
uv sync --locked
# Only copy if .env does not already exist.
Copy-Item .env.example .env
```

3. Edit `.env` locally. For the tested route, use:

```dotenv
LLM_PROVIDER=omniroute
OMNIROUTE_BASE_URL=http://localhost:20128/v1
OMNIROUTE_API_KEY=replace-with-your-own-key
OMNIROUTE_MODEL=cx/gpt-5.6-luna-low
EMBEDDING_BACKEND=local
LOCAL_EMBEDDING_PATH=data/models/embeddinggemma-300m
QDRANT_PATH=data/qdrant-gemma-pages
KB_PATH=Knowledge Base
```

**The localhost endpoint is not included in this repository.** Reviewers must run their own OmniRoute instance or configure another supported provider below. The application does not change OmniRoute server settings. The template may name an earlier mini-model route; select a model available on your endpoint, with strict JSON-schema support. The mini route encountered rate limits during development; Luna was used for the recorded evaluation.

4. Accept the [EmbeddingGemma model terms](https://huggingface.co/google/embeddinggemma-300m), authenticate, and download the model:

```powershell
uv run hf auth login
uv run python -m sop_assistant.download
```

The download is explicit, roughly 1.2 GB for the main weights, and requires internet/Hugging Face access. Embedding inference thereafter uses the downloaded snapshot locally.

5. Extract, inspect, index, and ask:

```powershell
uv run sop extract
# Inspect data/pages.json, particularly scan numbers and P1/SEV1 identifiers.
uv run sop ingest
uv run sop ask "Berapa target respons awal P1? Apakah harus selesai dalam 15 menit?"
```

The selected provider's API key must be configured even for local ingestion: the current CLI initializes the answering client alongside the embedding adapter. Local ingestion itself makes no LLM or hosted embedding request.

`uv run` handles the virtual environment; PowerShell activation or execution-policy changes are unnecessary. Repeating ingestion with an unchanged corpus skips embedding. Use a **new `QDRANT_PATH`** when changing documents or embedding/index configuration; existing indexes are not destructively rebuilt.

### Other answering providers

Keep `EMBEDDING_BACKEND=local` to retain local embeddings. Replace the LLM settings with either:

```dotenv
LLM_PROVIDER=openai
OPENAI_API_KEY=replace-with-your-own-key
OPENAI_MODEL=your-accessible-json-schema-model
```

or:

```dotenv
LLM_PROVIDER=openrouter
OPENROUTER_API_KEY=replace-with-your-own-key
OPENROUTER_MODEL=your-accessible-json-schema-model
```

Model access, structured-output compatibility, limits and billing depend on your provider. These alternatives are configurable but were not used for the reported comprehensive run. Free routes are not guaranteed to be available or compatible.

## Configuration and privacy

| Setting | Purpose |
| --- | --- |
| `LLM_PROVIDER` | `omniroute`, `openai`, or `openrouter`; code fallback is `openai` |
| `<PROVIDER>_API_KEY`, `<PROVIDER>_MODEL` | Your authorized answering credentials and model |
| `<PROVIDER>_BASE_URL` | Optional compatible endpoint override |
| `EMBEDDING_BACKEND` | Set `local` for the tested EmbeddingGemma configuration |
| `LOCAL_EMBEDDING_PATH` | Existing downloaded model directory |
| `QDRANT_PATH` | Persistent local index; use a distinct path for incompatible configurations |
| `KB_PATH` | SOP directory; defaults to `Knowledge Base` |
| `JUDGE_MODEL` | Optional evaluation-model override; otherwise uses the selected provider's model setting |

Shell environment variables take precedence over `.env`. Keep real keys only in local configuration. `.env`, `.claude/`, model weights, local databases, and generated `data/` artifacts are excluded from Git. Do not publish credential-bearing logs or screenshots.

With **local embeddings**, ingestion does not send SOP text to an embedding API. Answering sends the question and retrieved SOP text to the configured LLM endpoint; evaluation sends saved answers, references and evidence to its judge. Processing beyond a proxy depends on its upstream provider. Extraction, offline tests and Markdown conversion make no LLM calls. Model download contacts Hugging Face. Ragas telemetry is disabled by the evaluator. Hosted LLM/judge requests may incur charges.

## Architecture and decisions

```text
SOP PDFs -> native, layout-aware extraction -> OCR only for insufficient text
         -> whole-page chunks + source/page metadata
         -> local EmbeddingGemma -> persistent Qdrant (cosine)
Question -> local query embedding -> Qdrant retrieval (limit 16)
         -> structured LLM response -> citation-ID validation
         -> statements + trusted document/page citations
Saved answers -> optional Ragas/custom checks -> JSON -> offline Markdown report
```

- **Extraction:** PyMuPDF line coordinates handle the supplied two-column layout. A conditional PowerShell/WinRT OCR adapter handles scans without changing execution policy.
- **Chunking:** each supplied SOP is one short page and fits the model's 2,048-token input limit, so preserving the whole page keeps rules and exceptions together. The adapter checks prompted token length and rejects oversized input rather than silently truncating it. Automatic splitting/parent–child retrieval is not implemented.
- **Retrieval:** the limit is 16; this corpus has four page chunks, so every question receives all four pages, ordered by similarity. This favors coverage for a tiny corpus, not selective retrieval at scale.
- **Storage:** local Qdrant avoids a server dependency. Stable IDs and a corpus/configuration manifest protect repeat ingestion and detect stale/incomplete indexes. Only one process may access a given database path at a time.
- **Answers:** `answered`, `needs_clarification`, and `unsupported` distinguish response decisions. An English system prompt requests Indonesian output and cited factual statements. Strict JSON schema, local validation, and one bounded repair attempt handle malformed outputs. Filenames/pages come from stored metadata, not model invention.
- **Safety boundary:** evidence is treated as untrusted data. Existing citation IDs establish provenance, **not semantic truth**. The free-text message contract is prompted and evaluated, but not fully enforced semantically in code.

The CLI returns JSON containing statements, evidence IDs, resolved citations, retrieved context/scores, and latency for auditing.

## Tests

```powershell
uv run pytest -q
uv run ruff check src tests
uv run ruff format --check src tests
uv run pylint src/sop_assistant
```

Latest verified implementation run: **43 tests passed**, Ruff passed, Pylint **10.00/10**. Offline tests use synthetic PDFs, mocked model boundaries and temporary real Qdrant storage; no credentials or hosted calls are needed. This is not a claim of clean-machine verification.

## Demonstration and evaluation

Ten human-authored cases in `eval/questions.json` include answerable, ambiguous and unsupported questions with references and source annotations. To generate and evaluate a **new** run:

```powershell
# Local embeddings and hosted answering; requires ingestion and configured credentials.
uv run sop evaluate --output data/my-answers.json
# Additional hosted judge calls; optional evaluation dependencies.
uv run --group eval python -m sop_assistant.evaluation --input data/my-answers.json --output data/my-scores.json
# Offline conversion, no model calls.
uv run python -m sop_assistant.report --input data/my-scores.json --output data/my-report.md
```

Choose unused output filenames: the judge and Markdown converter refuse to overwrite existing results. The answer-generation command saves incrementally and can replace its selected output. A failed run may be partial; inspect completion counts and metric errors.

### Recorded result — 26 October 2026

| Measurement | Result |
| --- | ---: |
| Expected-status agreement | 10/10 |
| Faithfulness, factual statements across all statuses | 0.983 (10 cases) |
| Factual Correctness F1 | 0.800 (6 cases) |
| Context Precision / Recall | 0.606 / 1.000 (6 cases) |
| Response Relevancy | 0.811 (6 cases) |
| Structural citation coverage / ID validity / metadata | 1.000 each (10 cases) |
| Custom citation-support judge | 0.910 (10 case-level means) |
| Custom message-contract / decision-quality rubrics | 1.000 each (10 cases) |

These are separate measurements, **not a combined accuracy score**. Reference/retrieval metrics apply to expected-answerable cases. Faithfulness also checks factual statements in unsupported responses; pure absence notices are not forced into grounding scores. Skipped/errors/uncertain judgments are excluded from averages and displayed separately. Response Relevancy uses local EmbeddingGemma. Citation and behavioral rubrics are custom checks, not official Ragas metrics.

**Conclusion:** required evidence was available, and the uncited-message failure did not recur in this run. Some closure exceptions, multi-document citation support, and reference agreement need review. High recall is expected when all four pages are retrieved. Judge judgments are not independently verified truth, and these ten development questions are not a held-out production benchmark.

The [full report](docs/ragas-comprehensive-report.md) contains questions, cited answers, references and review reasons. [Evaluation notes](docs/evaluation.md) explain failures and priorities. Scores are bound to saved input hashes; historical generation metadata absent from those files is explicitly unknown. Changing prompts/answers requires new judging, not reusing old scores. Ragas 0.4's compatibility dependencies are isolated in the optional `eval` group.

## Limitations and next improvements

- **OCR:** Windows-only scan fallback; English recognizer substitutions such as `Pl`/`SEVI` remain in raw evidence. Verify scans visually. Portable Indonesian OCR is a future improvement.
- **PDF layout:** column ordering is a heuristic for the supplied PDFs, not a general layout engine; nonempty corrupted text layers may still require review.
- **Scale:** oversized pages fail clearly; no automatic long-document splitting, reranker or calibrated answerability threshold is implemented.
- **Grounding:** schema validation cannot guarantee entailment or prevent all prompt injection. Review policy-sensitive answers and flagged citations manually.
- **Deployment:** Qdrant local mode and a user-managed LLM endpoint are proof-of-concept choices, not a multi-user production architecture.
- **Evaluation:** expand held-out/adversarial cases and calibrate judges with independent human review before setting release thresholds. Generator/judge model correlation can bias scores.
- **Source ambiguity:** KB01 uses `Menunggu Informasi` in recording instructions but omits it from a later status list; the assistant should not invent a reconciliation.

For submission, provide the repository link and the readable demonstration report. No additional UI or deployment is needed to demonstrate the assignment requirements.
