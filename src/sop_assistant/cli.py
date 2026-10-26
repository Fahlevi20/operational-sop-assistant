"""Local CLI. Extraction is offline; ingest/ask/evaluate call OpenAI."""

import argparse
import hashlib
import json
import os
import sys
import time
from dataclasses import asdict
from pathlib import Path

from dotenv import load_dotenv

from sop_assistant.extraction import chunks_from_pages, extract_pdf
from sop_assistant.ocr import windows_ocr
from sop_assistant.provider import Provider
from sop_assistant.store import Index


def write_json(path, value):
    """Write human-readable UTF-8 artifacts."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")


def corpus(kb):
    """Read only the SOP directory, never the assignment brief."""
    paths = sorted(Path(kb).glob("*.pdf"))
    if not paths:
        raise ValueError("No PDFs found in KB_PATH; place the supplied SOPs there.")
    digest = hashlib.sha256()
    for path in paths:
        digest.update(path.name.encode())
        digest.update(path.read_bytes())
    return paths, digest.hexdigest()


def ask(question, index, provider):
    """Retrieve and answer while retaining auditable evidence and timing."""
    if not question.strip():
        raise ValueError("Question must not be empty.")
    started = time.perf_counter()
    evidence = index.search(provider.embed([question], query=True)[0], limit=16)
    answer = provider.answer(question, evidence)
    return dict(
        answer,
        question=question,
        evidence=evidence,
        latency_seconds=round(time.perf_counter() - started, 3),
    )


def main(argv=None):  # pylint: disable=too-many-locals,too-many-branches
    """Return a process status without exposing raw provider exceptions."""
    load_dotenv()
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("extract", "ingest", "ask", "evaluate"):
        command = sub.add_parser(name)
        command.add_argument("--kb", default=os.getenv("KB_PATH", "Knowledge Base"))
        if name == "extract":
            command.add_argument("--output", default="data/pages.json")
        if name == "ask":
            command.add_argument("question")
        if name == "evaluate":
            command.add_argument("--golden", default="eval/questions.json")
            command.add_argument("--output", default="data/evaluation.json")
    args = parser.parse_args(argv)
    try:
        paths, fingerprint = corpus(args.kb)
        if args.command == "extract":
            pages = [page for path in paths for page in extract_pdf(path, windows_ocr)]
            write_json(args.output, [asdict(page) for page in pages])
            for page in pages:
                print(f"{page.source} p.{page.number}: {page.method}, {len(page.text)} characters")
            return 0
        embedding_model = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
        dimensions = int(os.getenv("OPENAI_EMBEDDING_DIMENSIONS", "1536"))
        if os.getenv("EMBEDDING_BACKEND", "openai") == "local":
            embedding_model = "google/embeddinggemma-300m"
            dimensions = 768
        with Index(
            Path(os.getenv("QDRANT_PATH", "data/qdrant")), embedding_model, dimensions
        ) as index:
            if args.command == "ingest" and index.matches(fingerprint):
                print(f"Unchanged: {index.count()} chunks; no API requests.")
                return 0
            if args.command != "ingest" and not index.matches(fingerprint):
                raise ValueError("Missing or stale index; run ingest with a fresh QDRANT_PATH.")
            if args.command == "ingest" and index.manifest:
                raise ValueError("Corpus changed; choose a fresh QDRANT_PATH before ingest.")
            provider = Provider(embedding_model=embedding_model, dimensions=dimensions)
            if args.command == "ingest":
                pages = [page for path in paths for page in extract_pdf(path, windows_ocr)]
                chunks = chunks_from_pages(pages)
                count = index.ingest(chunks, provider.embed([c.text for c in chunks]), fingerprint)
                print(f"Indexed {count} chunks from {len(paths)} documents.")
            elif args.command == "ask":
                result = ask(args.question, index, provider)
                print(json.dumps(result, ensure_ascii=False, indent=2))
            else:
                cases = json.loads(Path(args.golden).read_text(encoding="utf-8"))
                results = []
                for case in cases:
                    result = ask(case["question"], index, provider)
                    results.append({"case": case, "result": result})
                    write_json(args.output, {"results": results, "usage": provider.usage})
                print(
                    f"Saved {len(results)} live cases to {args.output}; review factual correctness."
                )
        return 0
    except (ValueError, OSError, RuntimeError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
