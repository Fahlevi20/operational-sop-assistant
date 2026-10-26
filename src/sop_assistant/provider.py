"""Small OpenAI boundary with bounded retries and sanitized failures."""

import json
import os

from openai import OpenAI

from sop_assistant.qa import SYSTEM_PROMPT, Answer, validate_answer


class Provider:
    """Embedding and structured generation; no credentials are persisted here."""

    def __init__(
        self, api_key=None, embedding_model="text-embedding-3-small", model=None, dimensions=1536
    ):
        key = os.getenv("OPENAI_API_KEY", "") if api_key is None else api_key
        if not key or key == "replace-me":
            raise ValueError("Set OPENAI_API_KEY in the local .env file.")
        self.client = OpenAI(api_key=key, timeout=60, max_retries=2)
        self.embedding_model = embedding_model
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
        self.dimensions = dimensions
        self.usage = []

    def embed(self, texts):
        """Embed modest batches, preserving input order."""
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
        """Generate structured statements then resolve only known references."""
        try:
            result = self.client.beta.chat.completions.parse(
                model=self.model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {
                        "role": "user",
                        "content": json.dumps(
                            {"question": question, "evidence": evidence}, ensure_ascii=False
                        ),
                    },
                ],
                response_format=Answer,
            )
            if result.usage:
                self.usage.append(result.usage.model_dump())
            parsed = result.choices[0].message.parsed
            if parsed is None:
                raise ValueError("No structured response")
        except Exception:  # noqa: BLE001 -- sanitize the external SDK boundary, including payload errors
            raise ValueError(
                "Answer request failed or was refused. Check model access and connectivity."
            ) from None
        return validate_answer(parsed, evidence)
