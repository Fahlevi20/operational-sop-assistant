"""Keep offline tests independent of developer credentials and .env settings."""

import pytest


@pytest.fixture(autouse=True)
def isolated_configuration(monkeypatch):
    """Reset provider selection even when CLI dotenv loading occurred earlier."""
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    monkeypatch.setenv("EMBEDDING_BACKEND", "openai")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_MODEL", raising=False)
    monkeypatch.delenv("OMNIROUTE_MODEL", raising=False)
    monkeypatch.delenv("OMNIROUTE_BASE_URL", raising=False)
