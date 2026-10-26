from types import SimpleNamespace

import pytest

from sop_assistant.provider import Provider


def test_missing_key_has_safe_error(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(ValueError, match="OPENAI_API_KEY"):
        Provider(api_key="")


def test_embedding_order_and_dimensions():
    class Embeddings:
        def create(self, **kwargs):
            return SimpleNamespace(
                data=[
                    SimpleNamespace(index=1, embedding=[0.0, 1.0]),
                    SimpleNamespace(index=0, embedding=[1.0, 0.0]),
                ]
            )

    provider = Provider(api_key="test-only", dimensions=2)
    provider.client = SimpleNamespace(embeddings=Embeddings())
    assert provider.embed(["one", "two"]) == [[1.0, 0.0], [0.0, 1.0]]


def test_provider_does_not_leak_exception_secrets():
    class Embeddings:
        def create(self, **kwargs):
            raise RuntimeError("sk-test-secret")

    provider = Provider(api_key="test-only")
    provider.client = SimpleNamespace(embeddings=Embeddings())
    with pytest.raises(ValueError) as caught:
        provider.embed(["one"])
    assert "sk-test-secret" not in str(caught.value)
