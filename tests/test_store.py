import pytest

from sop_assistant.extraction import Chunk
from sop_assistant.store import Index


def test_qdrant_persistence_idempotency_and_manifest(tmp_path):
    chunk = Chunk(
        "00000000-0000-0000-0000-000000000001", "policy.pdf", 1, "Response", "15 minutes", "native"
    )
    with Index(tmp_path / "db", "fake", 3) as index:
        assert index.ingest([chunk], [[1.0, 0.0, 0.0]], "abc") == 1
        assert index.matches("abc")
        assert index.search([1.0, 0.0, 0.0])[0]["source"] == "policy.pdf"
        index.ingest([chunk], [[1.0, 0.0, 0.0]], "abc")
        assert index.count() == 1
        with pytest.raises(ValueError, match="changed"):
            index.ingest([chunk], [[1.0, 0.0, 0.0]], "different")
    with Index(tmp_path / "db", "fake", 3) as index:
        assert index.count() == 1
    with pytest.raises(ValueError, match="configuration"), Index(tmp_path / "db", "other-model", 3):
        pass


def test_lost_collection_is_not_current(tmp_path):
    chunk = Chunk("00000000-0000-0000-0000-000000000001", "p.pdf", 1, "Rule", "Text", "native")
    with Index(tmp_path / "db", "fake", 3) as index:
        index.ingest([chunk], [[1.0, 0.0, 0.0]], "abc")
        index.client.delete_collection("sop")
    with Index(tmp_path / "db", "fake", 3) as index:
        assert not index.matches("abc")


def test_partial_loss_blocks_search(tmp_path):
    from qdrant_client import models

    chunks = [
        Chunk(f"00000000-0000-0000-0000-00000000000{i}", "p.pdf", 1, "Rule", "Text", "native")
        for i in (1, 2)
    ]
    with Index(tmp_path / "db", "fake", 3) as index:
        index.ingest(chunks, [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0]], "abc")
        index.client.delete("sop", points_selector=models.PointIdsList(points=[chunks[0].id]))
        assert not index.matches("abc")
        with pytest.raises(ValueError, match="incomplete"):
            index.search([1.0, 0.0, 0.0])


def test_empty_index_rejected(tmp_path):
    with Index(tmp_path / "db", "fake", 3) as index, pytest.raises(ValueError, match="ingest"):
        index.search([1.0, 0.0, 0.0])
