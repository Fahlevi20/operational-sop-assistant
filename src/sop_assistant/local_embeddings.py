"""Offline CPU EmbeddingGemma inference from an already downloaded snapshot."""

from pathlib import Path


class LocalEmbeddings:  # pylint: disable=too-few-public-methods
    """Lazy model loading keeps CLI startup and hosted answering lightweight."""

    def __init__(self, path, dimensions=768, loader=None):
        self.path = Path(path)
        self.dimensions = dimensions
        self.loader = loader
        self.model = None

    def embed(self, texts, query=False):
        """Use model-configured query/document prompts and unit-length vectors."""
        if self.model is None:
            loader = self.loader
            if loader is None:
                from sentence_transformers import SentenceTransformer  # pylint: disable=import-outside-toplevel

                loader = SentenceTransformer
            self.model = loader(str(self.path), device="cpu", local_files_only=True)
        if self.loader is None:
            prefix = self.model.prompts.get("query" if query else "document", "")
            for text in texts:
                size = len(self.model.tokenizer(prefix + text, truncation=False)["input_ids"])
                if size > self.model.max_seq_length:
                    raise ValueError(
                        f"Embedding input has {size} tokens; limit is {self.model.max_seq_length}. "
                        "Split the document before indexing; truncation is disabled by validation."
                    )
        encode = self.model.encode_query if query else self.model.encode_document
        vectors = encode(
            texts,
            batch_size=2,
            normalize_embeddings=True,
            truncate_dim=self.dimensions,
            convert_to_numpy=True,
            show_progress_bar=False,
        )
        return vectors.tolist() if hasattr(vectors, "tolist") else vectors
