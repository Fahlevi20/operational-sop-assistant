from types import SimpleNamespace

import pytest

from sop_assistant.provider import Provider


def test_omniroute_explicit_schema_and_local_embeddings(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "omniroute")
    monkeypatch.setenv("OMNIROUTE_API_KEY", "test-only")
    monkeypatch.setenv("EMBEDDING_BACKEND", "local")
    provider = Provider()
    assert str(provider.client.base_url) == "http://localhost:20128/v1/"
    assert provider.model == "ddgw/gpt-5.4-mini"

    class Completions:
        def create(self, **kwargs):
            assert kwargs["response_format"]["type"] == "json_schema"
            schema = kwargs["response_format"]["json_schema"]["schema"]
            assert schema["additionalProperties"] is False
            assert set(schema["required"]) == set(schema["properties"])
            assert schema["$defs"]["Statement"]["additionalProperties"] is False
            return SimpleNamespace(
                usage=None,
                choices=[
                    SimpleNamespace(
                        message=SimpleNamespace(
                            content='{"status":"unsupported","statements":[],"message":"Not specified."}'
                        )
                    )
                ],
            )

    provider.client = SimpleNamespace(chat=SimpleNamespace(completions=Completions()))
    assert provider.answer("Unknown?", [])["status"] == "unsupported"


def test_answer_repairs_format_once_and_revalidates():
    responses = iter(
        [
            '{"answer":"wrong schema"}',
            '{"status":"unsupported","statements":[],"message":"Not specified."}',
        ]
    )

    class Completions:
        def create(self, **kwargs):
            return SimpleNamespace(
                usage=None,
                choices=[SimpleNamespace(message=SimpleNamespace(content=next(responses)))],
            )

    provider = Provider(api_key="test-only")
    provider.client = SimpleNamespace(chat=SimpleNamespace(completions=Completions()))
    assert provider.answer("Unknown?", [])["status"] == "unsupported"


def test_answer_stops_after_two_invalid_outputs():
    class Completions:
        def create(self, **kwargs):
            return SimpleNamespace(
                usage=None, choices=[SimpleNamespace(message=SimpleNamespace(content="{}"))]
            )

    provider = Provider(api_key="test-only")
    provider.client = SimpleNamespace(chat=SimpleNamespace(completions=Completions()))
    with pytest.raises(ValueError, match="schema"):
        provider.answer("Unknown?", [])


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
