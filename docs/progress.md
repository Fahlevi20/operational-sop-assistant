# Implementation progress

Plan: `C:/Users/rozak/.claude/plans/fluffy-exploring-bentley.md`

- Setup: uv project and lock, ignored credential/data paths, placeholder-only .env.example.
- Extraction: native text first and Windows OCR fallback; all four supplied pages extracted and inspected. Column-order regression test passes.
- Index: persistent local Qdrant tested with fake vectors; idempotent upsert and manifest/config mismatch tests pass.
- Answering: structured statuses and evidence-ID validation; provider failures sanitized; adapter tests pass without real credentials.
- Evaluation: 10 SOP-grounded golden cases; optional Ragas Faithfulness runner and pinned compatible LangChain stack. Metric construction smoke-tested without requests.
- Documentation: README and evaluation notes include actual results and live-test limitations.
- Latest full suite: 20 passed. Ruff clean. Pylint 10/10.
- Fresh independent code review running; findings not yet available.
- Live ingestion/QA/Ragas blocked: no API key in environment and no .env exists at last check. No SOP content transmitted.

## Decisions

- Ruling: no Git repository or worktree exists; implement in the supplied directory without initializing Git, committing, or publishing because those actions were not requested. Cost: no commit-based execution ledger until Git is initialized by user request.
- Ruling: use Windows OCR proven available on this machine; portable Tesseract alternative documented but not implemented. Cost: scan ingestion currently Windows-only.
- Ruling: default configurable answer/judge model gpt-4.1-mini; actual access and response compatibility must be verified live. Cost: default may need changing for the user's account.
- Ruling: Ragas imports legacy LangChain modules; pin compatible evaluation-only dependencies. Cost: additional optional evaluation dependencies and future upgrade work.
- Ruling: generated extraction is ignored; retain observed raw OCR spelling, document Pl/SEVI artifacts rather than silently alter evidence. Cost: retrieval/answers may need normalization after measured live tests.
