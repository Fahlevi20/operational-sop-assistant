"""Single-process persistent Qdrant index with configuration checks."""

import json
from dataclasses import asdict
from pathlib import Path

from qdrant_client import QdrantClient, models


class Index:
    """Own and close one local Qdrant client per command."""

    def __init__(self, path: Path, model: str, dimensions: int):
        path.mkdir(parents=True, exist_ok=True)
        self.manifest_path = path / "manifest.json"
        self.config = {"model": model, "dimensions": dimensions, "chunking": 1}
        self.manifest = None
        if self.manifest_path.exists():
            self.manifest = json.loads(self.manifest_path.read_text(encoding="utf-8"))
            if self.manifest["config"] != self.config:
                raise ValueError(
                    "Index configuration differs; choose a new QDRANT_PATH and ingest."
                )
        self.client = QdrantClient(path=str(path))
        if not self.client.collection_exists("sop"):
            self.manifest = None
            self.client.create_collection(
                "sop",
                vectors_config=models.VectorParams(
                    size=dimensions, distance=models.Distance.COSINE
                ),
            )

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.client.close()

    def matches(self, fingerprint: str) -> bool:
        """An unchanged corpus needs no new embedding requests."""
        return bool(
            self.manifest
            and self.manifest["fingerprint"] == fingerprint
            and self.manifest.get("count", 0) > 0
            and self.count() == self.manifest["count"]
        )

    def count(self) -> int:
        """Return indexed section count."""
        return self.client.count("sop", exact=True).count

    def ingest(self, chunks, vectors, fingerprint: str) -> int:
        """Upsert stable IDs, rejecting changed corpora rather than mixing versions."""
        if self.manifest and not self.matches(fingerprint):
            raise ValueError("Corpus changed; choose a new QDRANT_PATH and ingest.")
        if not chunks or len(chunks) != len(vectors):
            raise ValueError("Expected one embedding for each nonempty chunk.")
        points = [
            models.PointStruct(id=c.id, vector=v, payload=asdict(c))
            for c, v in zip(chunks, vectors, strict=True)
        ]
        self.client.upsert("sop", points=points, wait=True)
        self.manifest = {"config": self.config, "fingerprint": fingerprint, "count": len(points)}
        temporary = self.manifest_path.with_suffix(".tmp")
        temporary.write_text(json.dumps(self.manifest), encoding="utf-8")
        temporary.replace(self.manifest_path)
        return len(points)

    def search(self, vector, limit=8):
        """Return evidence with scores, not an answerability judgment."""
        if not self.manifest or not self.matches(self.manifest["fingerprint"]):
            raise ValueError("Index is empty or incomplete; run ingest first.")
        points = self.client.query_points("sop", query=vector, limit=limit).points
        return [dict(p.payload, score=p.score) for p in points]
