import json

from sop_assistant.cli import main


def test_extract_cli_without_key(tmp_path, capsys):
    import pymupdf

    kb = tmp_path / "kb"
    kb.mkdir()
    with pymupdf.open() as doc:
        page = doc.new_page()
        page.insert_text((50, 50), "1. Policy\nA useful policy with enough text.")
        doc.save(kb / "policy.pdf")
    assert main(["extract", "--kb", str(kb), "--output", str(tmp_path / "pages.json")]) == 0
    pages = json.loads((tmp_path / "pages.json").read_text(encoding="utf-8"))
    assert pages[0]["source"] == "policy.pdf"
    assert "native" in capsys.readouterr().out


def test_empty_kb_returns_error(tmp_path, capsys):
    assert main(["extract", "--kb", str(tmp_path), "--output", str(tmp_path / "out.json")]) == 1
    assert "No PDFs" in capsys.readouterr().err
