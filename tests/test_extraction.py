import pymupdf
import pytest

from sop_assistant.extraction import Page, chunks_from_pages, extract_pdf


def test_native_text_retains_source_and_sections(tmp_path):
    path = tmp_path / "policy.pdf"
    with pymupdf.open() as doc:
        page = doc.new_page()
        page.insert_text(
            (50, 60),
            "1. Response\nInitial response is 15 minutes.\n2. Closure\nP1 needs confirmation.",
        )
        doc.save(path)
    pages = extract_pdf(path)
    assert pages[0].method == "native"
    chunks = chunks_from_pages(pages)
    assert len(chunks) == 1
    assert chunks[0].source == "policy.pdf"
    assert chunks[0].page == 1
    assert "15 minutes" in chunks[0].text
    assert "confirmation" in chunks[0].text
    assert chunks == chunks_from_pages(pages)


def test_empty_native_page_uses_ocr(tmp_path):
    path = tmp_path / "scan.pdf"
    with pymupdf.open() as doc:
        doc.new_page()
        doc.save(path)
    pages = extract_pdf(path, ocr=lambda page: "1. Incident\nEscalate immediately.")
    assert pages[0].method == "ocr"
    assert "Escalate" in pages[0].text


def test_empty_ocr_is_not_silently_indexed(tmp_path):
    path = tmp_path / "empty.pdf"
    with pymupdf.open() as doc:
        doc.new_page()
        doc.save(path)
    with pytest.raises(ValueError, match="empty|usable"):
        extract_pdf(path, ocr=lambda page: "")


def test_columns_read_left_before_right(tmp_path):
    path = tmp_path / "columns.pdf"
    with pymupdf.open() as doc:
        page = doc.new_page(width=600, height=800)
        page.insert_text((40, 80), "1. Left first")
        page.insert_text((340, 80), "3. Right first")
        page.insert_text((40, 180), "2. Left second")
        page.insert_text((340, 180), "4. Right second")
        doc.save(path)
    text = extract_pdf(path)[0].text
    assert text.index("Left second") < text.index("Right first")


def test_unsectioned_page_keeps_text():
    chunks = chunks_from_pages([Page("a.pdf", 1, "A plain policy without headings.", "native")])
    assert len(chunks) == 1
    assert chunks[0].text == "A plain policy without headings."
