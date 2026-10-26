"""Page extraction and section chunks with original provenance."""

import re
import uuid
from dataclasses import dataclass
from pathlib import Path

import pymupdf


@dataclass(frozen=True)
class Page:
    """Text from one original PDF page."""

    source: str
    number: int
    text: str
    method: str


@dataclass(frozen=True)
class Chunk:
    """A section that can be cited independently."""

    id: str
    source: str
    page: int
    section: str
    text: str
    method: str


def native_text(page):
    """Prefer column order when blocks form a clear central gutter."""
    blocks = []
    for block in page.get_text("dict")["blocks"]:
        for line in block.get("lines", []):
            x0, y0, x1, y1 = line["bbox"]
            text = "".join(span["text"] for span in line["spans"])
            blocks.append((x0, y0, x1, y1, text))
    middle = page.rect.width / 2
    left = [b for b in blocks if b[2] <= middle + 12]
    right = [b for b in blocks if b[0] >= middle - 12]
    if left and right and len(left) + len(right) == len(blocks):
        blocks = sorted(left, key=lambda b: b[1]) + sorted(right, key=lambda b: b[1])
        return "\n".join(b[4] for b in blocks).strip()
    return page.get_text(sort=True).strip()


def extract_pdf(path: Path, ocr=None) -> list[Page]:
    """Use native text first; never silently discard an unreadable page."""
    pages = []
    with pymupdf.open(path) as document:
        for number, page in enumerate(document, 1):
            text = native_text(page)
            method = "native"
            if len(text.strip()) < 20:
                if ocr is None:
                    raise ValueError(f"{path.name} page {number}: no usable text; OCR required")
                text = ocr(page).strip()
                method = "ocr"
            if len(text) < 20:
                raise ValueError(f"{path.name} page {number}: empty or unusable extraction")
            pages.append(Page(path.name, number, text, method))
    if not pages:
        raise ValueError(f"{path.name}: empty PDF")
    return pages


def chunks_from_pages(pages: list[Page]) -> list[Chunk]:
    """Split numbered headings without separating rules from their exceptions."""
    chunks = []
    for page in pages:
        parts = re.split(r"(?m)(?=^\s*\d{1,2}[.)]\s+)", page.text)
        for index, text in enumerate(parts):
            text = text.strip()
            if not text:
                continue
            heading = text.splitlines()[0]
            identity = f"{page.source}:{page.number}:{index}:{text}"
            chunks.append(
                Chunk(
                    str(uuid.uuid5(uuid.NAMESPACE_URL, identity)),
                    page.source,
                    page.number,
                    heading,
                    text,
                    page.method,
                )
            )
    return chunks
