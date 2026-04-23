"""Project indexing orchestration for stage-3 pipeline."""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone

from pigmeu_never_forget.domain.enums import DocumentStatus
from pigmeu_never_forget.domain.models import IndexJobResult, ProjectContext, SourceDocument
from pigmeu_never_forget.services.analysis import AnalysisService
from pigmeu_never_forget.services.chunking import ChunkingService
from pigmeu_never_forget.services.embedding import EmbeddingService
from pigmeu_never_forget.services.ingestion import IngestionDiff, IngestionService, SourceSnapshot
from pigmeu_never_forget.services.memory_index import MemoryIndexService
from pigmeu_never_forget.services.vector_store import VectorStoreService
from pigmeu_never_forget.storage.sqlite import sqlite_cursor


class IndexingService:
    """Orchestrate incremental indexing for a single project."""

    def __init__(
        self,
        ingestion: IngestionService | None = None,
        analysis: AnalysisService | None = None,
        chunking: ChunkingService | None = None,
        embedding: EmbeddingService | None = None,
        vector_store: VectorStoreService | None = None,
        memory_index: MemoryIndexService | None = None,
    ) -> None:
        self.ingestion = ingestion or IngestionService()
        self.analysis = analysis or AnalysisService()
        self.chunking = chunking or ChunkingService()
        self.embedding = embedding or EmbeddingService()
        self.vector_store = vector_store or VectorStoreService()
        self.memory_index = memory_index or MemoryIndexService()

    def index_project(self, project: ProjectContext) -> IndexJobResult:
        """Run one incremental indexing cycle for a project."""
        snapshots = self.ingestion.build_snapshots(project)
        diff = self.ingestion.diff_snapshots(project, snapshots)
        indexed_chunks = 0
        updated_docs = 0
        deleted_docs = 0
        failed_docs = 0
        warnings: list[str] = []
        failed_paths: set[str] = set()
        renamed_successes: list[tuple[str, SourceSnapshot]] = []

        for checkpoint in diff.deleted:
            self._deactivate_document_path(project, checkpoint.path)
            deleted_docs += 1

        to_index: list[tuple[SourceSnapshot, str | None]] = (
            [(snapshot, None) for snapshot in diff.new]
            + [(snapshot, None) for snapshot in diff.modified]
            + [(snapshot, old_checkpoint.path) for old_checkpoint, snapshot in diff.renamed]
        )
        for snapshot, renamed_from in to_index:
            try:
                indexed_chunks += self._index_snapshot(project, snapshot)
                updated_docs += 1
                if renamed_from is not None:
                    renamed_successes.append((renamed_from, snapshot))
            except Exception as exc:
                failed_docs += 1
                failed_paths.add(snapshot.path)
                warnings.append(f"{snapshot.path}: {type(exc).__name__}")

        for old_path, _ in renamed_successes:
            self._deactivate_document_path(project, old_path)
            deleted_docs += 1

        successful_snapshots = [snapshot for snapshot in snapshots if snapshot.path not in failed_paths]
        checkpoint_diff = IngestionDiff(
            new=[snapshot for snapshot in diff.new if snapshot.path not in failed_paths],
            modified=[snapshot for snapshot in diff.modified if snapshot.path not in failed_paths],
            unchanged=diff.unchanged,
            deleted=diff.deleted,
            renamed=[
                (old_checkpoint, snapshot)
                for old_checkpoint, snapshot in diff.renamed
                if snapshot.path not in failed_paths
            ],
        )
        self.ingestion.persist_checkpoints(project, successful_snapshots, checkpoint_diff)
        self.memory_index.refresh_project_memory(project)
        return IndexJobResult(
            indexed_docs=updated_docs,
            indexed_chunks=indexed_chunks,
            updated_docs=updated_docs,
            deleted_docs=deleted_docs,
            failed_docs=failed_docs,
            warnings=warnings,
        )

    def index_text(
        self,
        project: ProjectContext,
        title: str,
        text: str,
        source_type: str = "inline_text",
        tags: list[str] | None = None,
    ) -> dict[str, object]:
        """Index raw inline text input without requiring a project source file."""
        clean_title = title.strip() or "inline_text"
        clean_text = text.strip()
        safe_title = self._sanitize_key(clean_title)
        inline_path = f"__inline__/{safe_title}.md"
        source_hash = self._hash_text(f"{clean_title}\n{clean_text}\n{source_type}")
        content_hash = self._hash_text(clean_text)
        document = SourceDocument(
            source_id=f"inline::{safe_title}",
            source_type=source_type,
            path=inline_path,
            title=clean_title,
            mime_type="text/markdown",
            raw_text=clean_text,
            metadata={"tags": tags or [], "inline": True},
        )
        chunks_created = self._index_document(
            project=project,
            path=inline_path,
            source_hash=source_hash,
            content_hash=content_hash,
            parser_version="inline_v1",
            document=document,
        )
        return {
            "doc_id": self._doc_id(project.project_id, inline_path),
            "path": inline_path,
            "chunks_created": chunks_created,
            "source_type": source_type,
        }

    def _index_snapshot(self, project: ProjectContext, snapshot: SourceSnapshot) -> int:
        return self._index_document(
            project=project,
            path=snapshot.path,
            source_hash=snapshot.source_hash,
            content_hash=snapshot.content_hash,
            parser_version=snapshot.parser_version,
            document=snapshot.document,
        )

    def _index_document(
        self,
        project: ProjectContext,
        path: str,
        source_hash: str,
        content_hash: str,
        parser_version: str,
        document: SourceDocument,
    ) -> int:
        doc = document
        analysis = self.analysis.analyze(doc)
        doc_id = self._doc_id(project.project_id, path)
        chunks = self.chunking.chunk_document(
            project=project,
            doc_id=doc_id,
            path=path,
            text=doc.raw_text,
            section_hint=analysis.doc_type,
        )
        embeddings = self.embedding.embed_chunks(project, chunks)
        point_map = self.vector_store.upsert(project, chunks, embeddings)

        with sqlite_cursor(project.state_db_path) as connection:
            connection.execute(
                """
                insert into documents(
                  doc_id, project_id, path, source_type, title, mime_type, source_hash, content_hash,
                  parser_version, status, last_seen_at, last_indexed_at, summary_short, summary_full, topics_json, metadata_json
                ) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                on conflict(doc_id) do update set
                  source_hash = excluded.source_hash,
                  content_hash = excluded.content_hash,
                  parser_version = excluded.parser_version,
                  status = excluded.status,
                  last_seen_at = excluded.last_seen_at,
                  last_indexed_at = excluded.last_indexed_at,
                  title = excluded.title,
                  mime_type = excluded.mime_type,
                  metadata_json = excluded.metadata_json
                """,
                (
                    doc_id,
                    project.project_id,
                    path,
                    doc.source_type,
                    doc.title,
                    doc.mime_type,
                    source_hash,
                    content_hash,
                    parser_version,
                    DocumentStatus.ACTIVE.value,
                    self._utcnow(),
                    self._utcnow(),
                    "",
                    "",
                    "[]",
                    "{}",
                ),
            )
            connection.execute("update chunks set active = 0 where doc_id = ?", (doc_id,))
            for chunk, embedding in zip(chunks, embeddings, strict=False):
                qdrant_point_id = point_map.get(chunk.chunk_id, "")
                connection.execute(
                    """
                    insert into chunks(
                      chunk_id, doc_id, chunk_hash, position, section, token_count, text_preview, body_ref,
                      summary_short, embedding_model, embedding_dim, qdrant_point_id, faiss_id, active, metadata_json
                    ) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    on conflict(chunk_id) do update set
                      chunk_hash = excluded.chunk_hash,
                      position = excluded.position,
                      section = excluded.section,
                      token_count = excluded.token_count,
                      text_preview = excluded.text_preview,
                      body_ref = excluded.body_ref,
                      embedding_model = excluded.embedding_model,
                      embedding_dim = excluded.embedding_dim,
                      qdrant_point_id = excluded.qdrant_point_id,
                      active = excluded.active,
                      metadata_json = excluded.metadata_json
                    """,
                    (
                        chunk.chunk_id,
                        chunk.doc_id,
                        str(chunk.metadata.get("chunk_hash", "")),
                        chunk.position,
                        chunk.section,
                        chunk.token_count,
                        chunk.text[:500],
                        f"doc:{chunk.doc_id}",
                        "",
                        embedding.model,
                        embedding.dimension,
                        qdrant_point_id,
                        None,
                        1,
                        "{}",
                    ),
                )
        self.memory_index.update_document_memory(
            project=project,
            doc_id=doc_id,
            path=path,
            document=doc,
            analysis=analysis,
        )
        return len(chunks)

    def _doc_id(self, project_id: str, path: str) -> str:
        safe = path.replace("/", "__")
        return f"{project_id}::{safe}"

    def _deactivate_document_path(self, project: ProjectContext, path: str) -> None:
        doc_id = self._doc_id(project.project_id, path)
        self.vector_store.delete_doc(project, doc_id)
        with sqlite_cursor(project.state_db_path) as connection:
            connection.execute(
                "update documents set status = ?, last_indexed_at = ? where doc_id = ?",
                (DocumentStatus.DELETED.value, self._utcnow(), doc_id),
            )
            connection.execute("update chunks set active = 0 where doc_id = ?", (doc_id,))

    def _utcnow(self) -> str:
        return datetime.now(tz=timezone.utc).isoformat()

    def _hash_text(self, value: str) -> str:
        return hashlib.sha256(value.encode("utf-8")).hexdigest()

    def _sanitize_key(self, value: str) -> str:
        safe = "".join(char.lower() if char.isalnum() else "_" for char in value.strip())
        compact = "_".join(segment for segment in safe.split("_") if segment)
        return compact or "inline_text"
