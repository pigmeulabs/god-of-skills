from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from pigmeu_never_forget.domain.models import ChunkRecord, EmbeddingRecord, ProjectContext
from pigmeu_never_forget.services.vector_store import VectorStoreService


def build_project_context(tmp_path: Path, backend: str = "qdrant") -> ProjectContext:
    project_root = tmp_path / "project-a"
    rag_path = project_root / ".rag"
    cache_dir = rag_path / "cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    return ProjectContext(
        project_id="project-a",
        project_name="project-a",
        root_path=project_root,
        rag_path=rag_path,
        project_config_path=rag_path / "project.yaml",
        prompts_config_path=rag_path / "prompts.yaml",
        state_db_path=rag_path / "state.db",
        memory_db_path=rag_path / "memory.db",
        faiss_dir=rag_path / "faiss",
        cache_dir=cache_dir,
        logs_dir=rag_path / "logs",
        qdrant_collection="kb_project-a",
        settings={
            "storage": {"vector_backend": backend, "qdrant_url": "http://qdrant:6333"},
            "project_settings": {
                "retrieval": {"context_budget_tokens": 1800},
                "models": {"answer_model": "mistral-small-latest"},
            },
        },
    )


@dataclass
class _FakeCollection:
    name: str


@dataclass
class _FakeCollections:
    collections: list[_FakeCollection]


@dataclass
class _FakePoint:
    payload: dict[str, object]
    score: float


class _FakeQdrantClient:
    def __init__(self) -> None:
        self.collections: set[str] = set()
        self.points: dict[str, dict[str, object]] = {}
        self.upsert_calls = 0
        self.delete_calls = 0

    def get_collections(self):
        return _FakeCollections(collections=[_FakeCollection(name=item) for item in sorted(self.collections)])

    def create_collection(self, collection_name: str, vectors_config):
        self.collections.add(collection_name)

    def upsert(self, collection_name: str, points, wait: bool):
        self.upsert_calls += 1
        for point in points:
            self.points[str(point["id"])] = point

    def search(self, collection_name: str, query_vector, limit: int, with_payload: bool):
        result = []
        for point in self.points.values():
            result.append(_FakePoint(payload=point["payload"], score=0.9))
        return result[:limit]

    def delete(self, collection_name: str, points_selector, wait: bool):
        self.delete_calls += 1
        for point_id in points_selector.get("points", []):
            self.points.pop(str(point_id), None)


def test_qdrant_backend_uses_remote_when_client_available(tmp_path: Path, monkeypatch) -> None:
    context = build_project_context(tmp_path, backend="qdrant")
    service = VectorStoreService()
    fake_client = _FakeQdrantClient()
    monkeypatch.setattr(service, "_get_qdrant_client", lambda project: fake_client)

    chunk = ChunkRecord(
        chunk_id="chunk-1",
        doc_id="doc-1",
        text="hello world",
        position=0,
        section="intro",
        token_count=3,
        metadata={"source_path": "docs/a.md", "chunk_hash": "hash-1"},
    )
    embedding = EmbeddingRecord(
        chunk_id="chunk-1",
        vector=[0.1, 0.2, 0.3, 0.4],
        model="mistral-embed",
        dimension=4,
        dtype="float32",
    )

    service.upsert(context, [chunk], [embedding])
    assert fake_client.upsert_calls == 1

    hits = service.search(context, [0.1, 0.2, 0.3, 0.4], top_k=3)
    assert len(hits) == 1
    assert hits[0].chunk_id == "chunk-1"

    removed = service.delete_doc(context, "doc-1")
    assert removed == 1
    assert fake_client.delete_calls == 1


def test_qdrant_backend_falls_back_to_local_when_client_unavailable(tmp_path: Path, monkeypatch) -> None:
    context = build_project_context(tmp_path, backend="qdrant")
    service = VectorStoreService()
    monkeypatch.setattr(service, "_get_qdrant_client", lambda project: None)

    chunk = ChunkRecord(
        chunk_id="chunk-1",
        doc_id="doc-1",
        text="refresh token flow",
        position=0,
        section="auth",
        token_count=4,
        metadata={"source_path": "docs/auth.md", "chunk_hash": "hash-1"},
    )
    embedding = EmbeddingRecord(
        chunk_id="chunk-1",
        vector=[0.2, 0.3, 0.4, 0.5],
        model="mistral-embed",
        dimension=4,
        dtype="float32",
    )

    service.upsert(context, [chunk], [embedding])
    hits = service.search(context, [0.2, 0.3, 0.4, 0.5], top_k=1)
    assert len(hits) == 1
    assert hits[0].doc_id == "doc-1"
