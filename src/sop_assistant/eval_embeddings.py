"""Optional Ragas adapter for local query-to-query similarity embeddings."""

import asyncio
import os
import threading

from sop_assistant.local_embeddings import LocalEmbeddings


def evaluation_embeddings():
    """Load the optional base only for explicit evaluation, never hosted embeddings."""
    from ragas.embeddings.base import BaseRagasEmbedding  # pylint: disable=import-outside-toplevel

    class QueryEmbeddings(BaseRagasEmbedding):
        """Serialize CPU loading/inference; use identical prompts for both questions."""

        def __init__(self):
            super().__init__()
            self.local = LocalEmbeddings(
                os.getenv("LOCAL_EMBEDDING_PATH", "data/models/embeddinggemma-300m")
            )
            self.lock = threading.Lock()

        def embed_text(self, text, **kwargs):
            with self.lock:
                return self.local.embed([text], query=True)[0]

        async def aembed_text(self, text, **kwargs):
            return await asyncio.to_thread(self.embed_text, text, **kwargs)

    return QueryEmbeddings()
