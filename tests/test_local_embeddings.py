from sop_assistant.local_embeddings import LocalEmbeddings


def test_local_embedding_uses_distinct_query_document_prompts(tmp_path):
    calls = []

    class Model:
        def encode_query(self, texts, **kwargs):
            calls.append(("query", kwargs))
            return [[1.0, 0.0]]

        def encode_document(self, texts, **kwargs):
            calls.append(("document", kwargs))
            return [[0.0, 1.0]]

    adapter = LocalEmbeddings(tmp_path, dimensions=2, loader=lambda *a, **k: Model())
    assert adapter.embed(["question"], query=True) == [[1.0, 0.0]]
    assert adapter.embed(["document"]) == [[0.0, 1.0]]
    assert [c[0] for c in calls] == ["query", "document"]
    assert all(c[1]["normalize_embeddings"] for c in calls)
