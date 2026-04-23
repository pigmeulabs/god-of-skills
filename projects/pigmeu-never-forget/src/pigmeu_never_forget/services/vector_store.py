"""Vector store service with local cache mirror for stage-3 development."""

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path

from pigmeu_never_forget.domain.models import ChunkRecord, EmbeddingRecord, ProjectContext, RetrievalHit


@dataclass(slots=True)
class VectorPoint:
    """Local vector point representation."""

    point_id: str
    chunk_id: str
    doc_id: str
    vector: list[float]
    payload: dict[str, object]


class VectorStoreService:
    """Persist and retrieve chunk embeddings.

    This stage persists a local mirror under `.rag/cache/vector_index.json` so
    retrieval and reconciliation can run without an external dependency.
    """

    def upsert(
        self,
        project: ProjectContext,
        chunks: list[ChunkRecord],
        embeddings: list[EmbeddingRecord],
    ) -> dict[str, str]:
        """Upsert chunk embeddings and return `chunk_id -> point_id` mapping."""
        chunk_by_id = {chunk.chunk_id: chunk for chunk in chunks}
        index_path = project.cache_dir / "vector_index.json"
        index = self._load_index(index_path)
        for embedding in embeddings:
            chunk = chunk_by_id.get(embedding.chunk_id)
            if chunk is None:
                continue
            point_id = f"{project.project_id}:{embedding.chunk_id}"
            index[point_id] = VectorPoint(
                point_id=point_id,
                chunk_id=chunk.chunk_id,
                doc_id=chunk.doc_id,
                vector=embedding.vector,
                payload={
                    "doc_id": chunk.doc_id,
                    "chunk_id": chunk.chunk_id,
                    "source_path": str(chunk.metadata.get("source_path", "")),
                    "section": chunk.section or "",
                    "text": chunk.text,
                    "chunk_hash": str(chunk.metadata.get("chunk_hash", "")),
                    "content_type": str(chunk.metadata.get("content_type", "")),
                },
            )
        self._save_index(index_path, index)

        chunk_point_map = {
            point.chunk_id: point.point_id
            for point in index.values()
            if point.chunk_id in chunk_by_id
        }
        if self._backend(project) == "qdrant":
            self._try_qdrant_upsert(project, chunks, embeddings, chunk_point_map)
        return chunk_point_map

    def search(self, project: ProjectContext, query_vector: list[float], top_k: int) -> list[RetrievalHit]:
        """Search the local vector index using cosine similarity."""
        if top_k <= 0:
            return []
        if self._backend(project) == "qdrant":
            remote_hits = self._try_qdrant_search(project, query_vector=query_vector, top_k=top_k)
            if remote_hits is not None:
                return remote_hits
        index = self._load_index(project.cache_dir / "vector_index.json")
        ranked = sorted(
            (
                (
                    self._cosine_similarity(query_vector, point.vector),
                    point,
                )
                for point in index.values()
            ),
            key=lambda item: item[0],
            reverse=True,
        )
        hits: list[RetrievalHit] = []
        for score, point in ranked[:top_k]:
            hits.append(
                RetrievalHit(
                    doc_id=point.doc_id,
                    chunk_id=point.chunk_id,
                    score=score,
                    path=str(point.payload.get("source_path", "")),
                    section=str(point.payload.get("section", "")) or None,
                    preview=str(point.payload.get("text", ""))[:200],
                )
            )
        return hits

    def delete_doc(self, project: ProjectContext, doc_id: str) -> int:
        """Delete all points for a document and return removed count."""
        path = project.cache_dir / "vector_index.json"
        index = self._load_index(path)
        before = len(index)
        removed_point_ids = [point_id for point_id, point in index.items() if point.doc_id == doc_id]
        index = {point_id: point for point_id, point in index.items() if point.doc_id != doc_id}
        self._save_index(path, index)
        if self._backend(project) == "qdrant":
            self._try_qdrant_delete(project, removed_point_ids)
        return before - len(index)

    def _load_index(self, path: Path) -> dict[str, VectorPoint]:
        if not path.exists():
            return {}
        raw = json.loads(path.read_text(encoding="utf-8"))
        result: dict[str, VectorPoint] = {}
        for row in raw:
            point = VectorPoint(
                point_id=row["point_id"],
                chunk_id=row["chunk_id"],
                doc_id=row["doc_id"],
                vector=row["vector"],
                payload=row["payload"],
            )
            result[point.point_id] = point
        return result

    def _save_index(self, path: Path, points: dict[str, VectorPoint]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = [
            {
                "point_id": point.point_id,
                "chunk_id": point.chunk_id,
                "doc_id": point.doc_id,
                "vector": point.vector,
                "payload": point.payload,
            }
            for point in points.values()
        ]
        path.write_text(json.dumps(payload, ensure_ascii=True), encoding="utf-8")

    def _cosine_similarity(self, left: list[float], right: list[float]) -> float:
        if not left or not right:
            return 0.0
        size = min(len(left), len(right))
        dot = sum(left[i] * right[i] for i in range(size))
        left_norm = math.sqrt(sum(value * value for value in left[:size]))
        right_norm = math.sqrt(sum(value * value for value in right[:size]))
        if left_norm == 0 or right_norm == 0:
            return 0.0
        return dot / (left_norm * right_norm)

    def _backend(self, project: ProjectContext) -> str:
        return str(project.settings.get("storage", {}).get("vector_backend", "local")).lower()

    def _try_qdrant_upsert(
        self,
        project: ProjectContext,
        chunks: list[ChunkRecord],
        embeddings: list[EmbeddingRecord],
        chunk_point_map: dict[str, str],
    ) -> None:
        client = self._get_qdrant_client(project)
        if client is None or not embeddings:
            return
        self._ensure_qdrant_collection(client, project, vector_size=embeddings[0].dimension)
        points = []
        chunk_by_id = {chunk.chunk_id: chunk for chunk in chunks}
        for embedding in embeddings:
            chunk = chunk_by_id.get(embedding.chunk_id)
            if chunk is None:
                continue
            point_id = chunk_point_map.get(embedding.chunk_id, f"{project.project_id}:{embedding.chunk_id}")
            payload = {
                "doc_id": chunk.doc_id,
                "chunk_id": chunk.chunk_id,
                "source_path": str(chunk.metadata.get("source_path", "")),
                "section": chunk.section or "",
                "text": chunk.text,
                "chunk_hash": str(chunk.metadata.get("chunk_hash", "")),
                "content_type": str(chunk.metadata.get("content_type", "")),
            }
            points.append({"id": point_id, "vector": embedding.vector, "payload": payload})
        if not points:
            return
        try:
            client.upsert(collection_name=project.qdrant_collection, points=points, wait=True)
        except Exception:
            # Keep local mirror as source of continuity.
            return

    def _try_qdrant_search(
        self,
        project: ProjectContext,
        query_vector: list[float],
        top_k: int,
    ) -> list[RetrievalHit] | None:
        client = self._get_qdrant_client(project)
        if client is None:
            return None
        try:
            points = client.search(
                collection_name=project.qdrant_collection,
                query_vector=query_vector,
                limit=top_k,
                with_payload=True,
            )
        except Exception:
            return None
        hits: list[RetrievalHit] = []
        for point in points:
            payload = dict(getattr(point, "payload", {}) or {})
            hits.append(
                RetrievalHit(
                    doc_id=str(payload.get("doc_id", "")),
                    chunk_id=str(payload.get("chunk_id", "")),
                    score=float(getattr(point, "score", 0.0)),
                    path=str(payload.get("source_path", "")),
                    section=str(payload.get("section", "")) or None,
                    preview=str(payload.get("text", ""))[:200],
                )
            )
        return hits

    def _try_qdrant_delete(self, project: ProjectContext, point_ids: list[str]) -> None:
        if not point_ids:
            return
        client = self._get_qdrant_client(project)
        if client is None:
            return
        try:
            client.delete(collection_name=project.qdrant_collection, points_selector={"points": point_ids}, wait=True)
        except Exception:
            return

    def _get_qdrant_client(self, project: ProjectContext):
        try:
            from qdrant_client import QdrantClient
        except Exception:
            return None
        qdrant_url = str(project.settings.get("storage", {}).get("qdrant_url", "")).strip()
        if not qdrant_url:
            return None
        try:
            return QdrantClient(url=qdrant_url, timeout=2.0)
        except Exception:
            return None

    def _ensure_qdrant_collection(self, client, project: ProjectContext, vector_size: int) -> None:
        try:
            collections = client.get_collections()
            names = {item.name for item in collections.collections}
            if project.qdrant_collection in names:
                return
            try:
                from qdrant_client.http import models as qmodels
                vectors_config = qmodels.VectorParams(size=vector_size, distance=qmodels.Distance.COSINE)
                client.create_collection(collection_name=project.qdrant_collection, vectors_config=vectors_config)
                return
            except Exception:
                client.create_collection(collection_name=project.qdrant_collection, vectors_config={"size": vector_size, "distance": "Cosine"})
        except Exception:
            return
