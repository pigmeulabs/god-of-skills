"""Deterministic embedding service used for local-first development."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass

from pigmeu_never_forget.domain.models import ChunkRecord, EmbeddingRecord, ProjectContext


@dataclass(slots=True)
class EmbeddingSettings:
    """Resolved embedding settings."""

    model: str
    dimension: int
    dtype: str


class EmbeddingService:
    """Generate deterministic embeddings for local testability."""

    def embed_chunks(self, project: ProjectContext, chunks: list[ChunkRecord]) -> list[EmbeddingRecord]:
        """Embed chunk texts using a deterministic pseudo-vector representation."""
        settings = self._resolve(project)
        return [
            EmbeddingRecord(
                chunk_id=chunk.chunk_id,
                vector=self._vectorize(chunk.text, settings.dimension),
                model=settings.model,
                dimension=settings.dimension,
                dtype=settings.dtype,
            )
            for chunk in chunks
        ]

    def embed_query(self, project: ProjectContext, text: str) -> list[float]:
        """Embed query text using the same deterministic method."""
        settings = self._resolve(project)
        return self._vectorize(text, settings.dimension)

    def _resolve(self, project: ProjectContext) -> EmbeddingSettings:
        model = str(project.settings["project_settings"]["models"]["embedding_model"])
        return EmbeddingSettings(model=model, dimension=64, dtype="float32")

    def _vectorize(self, text: str, dimension: int) -> list[float]:
        values: list[float] = []
        seed = text.encode("utf-8")
        counter = 0
        while len(values) < dimension:
            digest = hashlib.sha256(seed + counter.to_bytes(4, "big")).digest()
            for index in range(0, len(digest), 4):
                if len(values) >= dimension:
                    break
                raw = int.from_bytes(digest[index : index + 4], "big")
                values.append((raw / 2**32) * 2.0 - 1.0)
            counter += 1
        return values
