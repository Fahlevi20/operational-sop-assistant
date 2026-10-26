# Operational SOP Assistant

A document-grounded AI assistant for operational SOPs, built with Python and Qdrant, with source citations and safe handling of unsupported questions.

Recruitment proof of concept for PT Inti Nya Teknologi. Runs locally as a CLI with CPU EmbeddingGemma embeddings and local Qdrant. Answering uses a configurable OpenAI-compatible endpoint; the current local setup uses OmniRoute with `ddgw/gpt-5.4-mini`. No Docker, GPU, or frontend required.

## Development status

Work in progress, not the final recruitment submission. Local EmbeddingGemma CPU inference and ingestion have been verified. OmniRoute answering is integrated; full golden evaluation and Ragas validation are in progress. The route passed synthetic tests but ignored the JSON-schema parameter on a real-evidence request, so schema instructions are also included explicitly in the prompt and all output is locally validated. Model identity, availability, and costs are controlled by the user's provider, not inferred from route names.

HR has approved a public repository. Supplied PDFs remain excluded from this initial code snapshot; reviewers can place the supplied SOPs in `Knowledge Base/`.

## Quick start (PowerShell)

Prerequisites: Python 3.11+, [uv](https://docs.astral.sh/uv/), downloaded EmbeddingGemma weights, and an authorized OpenAI-compatible LLM endpoint (OmniRoute in the tested local configuration). The included scan OCR adapter requires Windows with an installed OCR language pack. Tested locally with Windows 11 and Python 3.13.

```powershell
uv sync --locked
Copy-Item .env.example .env
# Edit .env locally and set OMNIROUTE_API_KEY. Keep OmniRoute running.
# Accept Gemma terms on Hugging Face, then:
uv run hf auth login
uv run python -m sop_assistant.download
uv run sop extract
# Inspect data/pages.json, especially numbers and identifiers from scans.
uv run sop ingest
uv run sop ask "Berapa target respons awal P1? Apakah harus selesai dalam 15 menit?"
```

Put the four supplied SOP PDFs under `Knowledge Base/` (or set `KB_PATH`). Original recruiting PDFs are intentionally excluded from Git pending permission to redistribute. Reviewers need their own supplied copy. Do not put the assignment brief in the knowledge-base folder.

Activation of `.venv` is unnecessary: `uv run` uses the project environment automatically. `uv.lock` records exact dependencies.

## Configuration and credential hygiene

Copy `.env.example` once; do not overwrite an existing `.env`. Environment variables already present in the shell take precedence over `.env`.

| Variable | Default | Purpose |
|---|---|---|
| `OPENAI_API_KEY` | none | Required for ingest, ask, and live evaluation |
| `OPENAI_MODEL` | `gpt-4.1-mini` | Structured-output answering model; verify account access |
| `OPENAI_EMBEDDING_MODEL` | `text-embedding-3-small` | Embedding model |
| `OPENAI_EMBEDDING_DIMENSIONS` | `1536` | Qdrant vector dimension |
| `QDRANT_PATH` | `data/qdrant` | Persistent local database directory |
| `KB_PATH` | `Knowledge Base` | SOP PDF directory |
| `OPENAI_JUDGE_MODEL` | `gpt-4.1-mini` | Ragas judge model |

`.env`, `.venv/`, extracted text, vectors, and generated evaluation output are ignored. The program does not log API keys; provider errors are sanitized. Do not commit screenshots or logs containing credentials. The golden set includes SOP-derived references and should remain in the private repository until sharing permission is clarified.

**Data flow and billing:** ingestion sends all extracted SOP chunks to OpenAI for embedding. Questions and retrieved chunks are sent for answering. Ragas judging sends saved answers and contexts to OpenAI again. These commands use paid API requests; extraction and offline tests do not. No document content is sent by `extract`. Ragas telemetry is disabled in the judge runner.

## Architecture

```text
SOP PDFs -> native/layout-aware extraction -> OCR only for empty text pages
         -> numbered-section chunks + filename/page/heading metadata
         -> OpenAI embeddings -> persistent local Qdrant
Question -> embedding -> top-8 retrieval -> structured OpenAI answer
         -> validate evidence IDs -> statements + trusted document/page citations
```

- **Extraction:** PyMuPDF reads text and positional lines. A central-gutter heuristic preserves column order. Image-only pages use Windows OCR via an in-memory PowerShell/WinRT bridge. No execution-policy change is needed.
- **Chunking:** SOP numbered sections keep rules and exceptions together. Stable UUIDs preserve provenance. This is optimized for the provided short SOPs, not arbitrary long documents.
- **Storage:** actual Qdrant client local persistent mode, cosine similarity. No server process is needed. Only one process may use the same directory at a time.
- **Reproducibility:** a manifest records source hashes, embedding model, dimensions, and chunking version. Unchanged ingestion skips API calls. Changed source/configuration requires a new `QDRANT_PATH`; the CLI does not delete old data automatically.
- **Answering:** structured statuses distinguish `answered`, `needs_clarification`, and `unsupported`. Each substantive statement references retrieved evidence. Citation filenames/pages are resolved from stored metadata rather than trusted from model output.
- **Safety:** retrieved text is untrusted evidence, not instructions. Missing information should produce abstention rather than invented policy. API failures are operational errors, not unsupported answers.

The JSON answer includes statements, evidence IDs, resolved citations, retrieved text/scores, and latency for auditability. Reference validation does **not** prove semantic entailment; factual correctness needs evaluation.

## Tests and quality

```powershell
uv run pytest -q
uv run ruff check src tests
uv run ruff format --check src tests
uv run pylint src/sop_assistant
```

Offline tests use synthetic PDFs, mocked API boundaries, and real temporary local Qdrant storage. They require no key and do not call OpenAI. Pylint is applied to application code; Ruff also checks tests. Narrow lint suppressions document the CLI dispatcher complexity and the sanitized external SDK boundary.

## Golden set and live evaluation

`eval/questions.json` contains ten hand-authored Indonesian questions with expected status, reference answer, and source page/section. Cases cover answerable, cross-document, ambiguous, and unsupported requests. They are a development set, not a held-out benchmark.

```powershell
# Requires configured key and a completed ingestion. Makes embedding + LLM calls.
uv run sop evaluate
# Additional paid LLM judge calls; optional dependencies are separate.
uv sync --locked --group eval
uv run --group eval python -m sop_assistant.evaluation --input data/evaluation-english-prompt.json --output data/ragas-comprehensive.json
# Offline conversion: no model calls. Choose a new output filename on repeat runs.
uv run python -m sop_assistant.report --input data/ragas-comprehensive.json --output data/ragas-comprehensive.md
```

Select the actual generation file you want to evaluate; the example uses the saved English-prompt experiment. The evaluator measures **Faithfulness**, **Factual Correctness F1**, **Context Precision**, **Context Recall**, and **Response Relevancy** (Ragas `AnswerRelevancy`). Relevancy uses local EmbeddingGemma, not hosted embeddings. It also records deterministic citation coverage/validity/metadata checks and custom model-judged citation support, uncited-message checks, and answer/abstention/clarification quality. Custom checks are not official Ragas metrics.

Reference correctness and retrieval metrics apply to expected-answerable cases. Faithfulness evaluates factual statements across all statuses; pure absence notices do not receive fabricated grounding scores. Skipped, uncertain and failed measurements remain explicit and are excluded from means. Expected-status agreement remains separate from answer quality.

Results are checkpointed with source-file SHA256, judge configuration, metric settings and completion counts. Historical generation configuration that was not recorded is marked unknown. Existing outputs are not overwritten. Evaluation makes additional judge requests and can encounter rate limits or charges; Markdown conversion is offline. The report includes per-case answers/citations, metric explanations and review findings without blending unrelated metrics into one overall score.

Ragas 0.4 imports legacy LangChain modules, so the evaluation group pins compatible LangChain versions. This keeps the heavier evaluation stack separate from the application.

Review every result for factual support, complete exceptions, citation correctness, retrieval coverage, and refusal quality. Do not treat a valid reference or high judge score as proof of correctness. See [evaluation notes](docs/evaluation.md).

## Known limitations

- Scan OCR currently requires Windows. A portable deployment should add Tesseract with Indonesian language data or another tested OCR adapter. This alternative is not implemented here.
- The available Windows recognizer may be English. Observed raw OCR substitutions include `Pl` for `P1` and `SEVI` for `SEV1`. Extracted text is retained without silently rewriting source evidence. Check scans visually before relying on high-stakes answers.
- Column detection is a heuristic for the provided layout, not general document layout understanding. Sparse/corrupted text layers may need manual review even if they pass the minimum text-length check.
- Exact section splitting assumes numbered SOP headings; long-document token-aware splitting is not implemented.
- Top-8 dense retrieval may miss evidence or retrieve unrelated sections. No reranker or calibrated answerability threshold is claimed.
- Prompting and structural citation validation reduce—but cannot eliminate—hallucinations or prompt injection.
- Qdrant local mode is single-process and is not a production service architecture.
- Models are configurable; API availability, network access, rate limits, and charges remain external dependencies.
- KB01 contains a status-list inconsistency: `Menunggu Informasi` appears in recording instructions but not the later enumerated statuses. The assistant should not invent a reconciliation.

## Submission

Keep the repository private until HR confirms sharing permissions and reviewer access. Submit the repository link plus actual demonstration/evaluation outputs before **27 October 2026, 11:00** in the timezone agreed with HR. A private link alone does not grant access. No remote repository is created or published by this project.
