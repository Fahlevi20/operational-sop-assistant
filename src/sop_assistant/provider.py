"""Small OpenAI boundary with bounded retries and sanitized failures."""

import json
import os

from openai import OpenAI, pydantic_function_tool

from sop_assistant.qa import SYSTEM_PROMPT, Answer, validate_answer


class Provider:
    """Embedding and structured generation; no credentials are persisted here."""

    def __init__(
        self, api_key=None, embedding_model="text-embedding-3-small", model=None, dimensions=1536
    ):
        route = os.getenv("LLM_PROVIDER", "openai").upper()
        if route not in {"OPENAI", "OPENROUTER", "OMNIROUTE"}:
            raise ValueError("LLM_PROVIDER must be openai, openrouter, or omniroute.")
        key_name = f"{route}_API_KEY"
        key = os.getenv(key_name, "") if api_key is None else api_key
        if not key or key == "replace-me":
            raise ValueError(f"Set {key_name} in the local .env file.")
        defaults = {
            "OPENAI": "https://api.openai.com/v1",
            "OPENROUTER": "https://openrouter.ai/api/v1",
            "OMNIROUTE": "http://localhost:20128/v1",
        }
        self.client = OpenAI(
            api_key=key,
            base_url=os.getenv(f"{route}_BASE_URL", defaults[route]),
            timeout=90,
            max_retries=2,
        )
        self.embedding_model = embedding_model
        default_model = "ddgw/gpt-5.4-mini" if route == "OMNIROUTE" else "gpt-4.1-mini"
        self.model = model or os.getenv(f"{route}_MODEL", default_model)
        self.local = None
        if os.getenv("EMBEDDING_BACKEND", "openai") == "local":
            from sop_assistant.local_embeddings import LocalEmbeddings  # pylint: disable=import-outside-toplevel

            self.local = LocalEmbeddings(
                os.getenv("LOCAL_EMBEDDING_PATH", "data/models/embeddinggemma-300m"), dimensions
            )
        self.dimensions = dimensions
        self.usage = []

    def embed(self, texts, query=False):  # pylint: disable=unused-argument
        """Embed modest batches, preserving input order."""
        if self.local:
            return self.local.embed(texts, query=query)
        vectors = []
        try:
            for start in range(0, len(texts), 32):
                batch = texts[start : start + 32]
                result = self.client.embeddings.create(
                    model=self.embedding_model, input=batch, dimensions=self.dimensions
                )
                ordered = sorted(result.data, key=lambda item: item.index)
                if len(ordered) != len(batch):
                    raise ValueError("Embedding count mismatch")
                for item in ordered:
                    if len(item.embedding) != self.dimensions:
                        raise ValueError("Embedding dimensions mismatch")
                    vectors.append(item.embedding)
                usage = getattr(result, "usage", None)
                if usage:
                    self.usage.append(usage.model_dump())
        except Exception:  # noqa: BLE001 -- sanitize the external SDK boundary, including payload errors
            raise ValueError(
                "Embedding request failed. Check API access, quota, and connectivity."
            ) from None
        return vectors

    def answer(self, question, evidence):
        """One format-repair attempt; never return an unvalidated claim."""
        schema = pydantic_function_tool(Answer)["function"]["parameters"]
        messages = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT
                + " Return ONLY JSON matching this exact schema: "
                + json.dumps(schema),
            },
            {
                "role": "user",
                "content": json.dumps(
                    {"question": question, "evidence": evidence}, ensure_ascii=False
                ),
            },
        ]
        for attempt in range(2):
            try:
                result = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    response_format={
                        "type": "json_schema",
                        "json_schema": {"name": "Answer", "strict": True, "schema": schema},
                    },
                )
            except Exception as error:  # noqa: BLE001 -- sanitize external SDK errors
                status = getattr(error, "status_code", None)
                detail = f"HTTP {status}" if isinstance(status, int) else type(error).__name__
                raise ValueError(
                    f"LLM request failed ({detail}); check endpoint access and limits."
                ) from None
            if result.usage:
                self.usage.append(result.usage.model_dump())
            try:
                parsed = Answer.model_validate_json(result.choices[0].message.content or "")
                return validate_answer(parsed, evidence)
            except (ValueError, IndexError, TypeError):
                if attempt:
                    raise ValueError(
                        "LLM output failed schema/citation validation after one repair retry."
                    ) from None
                messages.append(
                    {
                        "role": "user",
                        "content": "Previous output failed schema or citation validation. "
                        "Regenerate from the original evidence. "
                        "Use status, statements (text and evidence_ids), and message exactly. "
                        "Every evidence_id must exist in the provided evidence; "
                        "answered message must be empty.",
                    }
                )
        raise ValueError("LLM output validation failed.")
