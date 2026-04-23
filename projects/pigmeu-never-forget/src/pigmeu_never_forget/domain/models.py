"""Domain dataclasses aligned with the architecture docs."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from pigmeu_never_forget.domain.enums import JobStatus, JobType, LockType


@dataclass(slots=True)
class WorkspacePaths:
    """Resolved workspace-level paths."""

    root_path: Path
    metadata_path: Path
    config_path: Path
    credentials_path: Path
    registry_db_path: Path
    logs_path: Path


@dataclass(slots=True)
class ProjectContext:
    """Resolved project-level paths and settings."""

    project_id: str
    project_name: str
    root_path: Path
    rag_path: Path
    project_config_path: Path
    prompts_config_path: Path
    state_db_path: Path
    memory_db_path: Path
    faiss_dir: Path
    cache_dir: Path
    logs_dir: Path
    qdrant_collection: str
    settings: dict[str, Any]


@dataclass(slots=True)
class SourceDocument:
    """Canonical normalized source document."""

    source_id: str
    source_type: str
    path: str | None
    title: str | None
    mime_type: str | None
    raw_text: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class ChunkRecord:
    """Chunked retrieval unit."""

    chunk_id: str
    doc_id: str
    text: str
    position: int
    section: str | None
    token_count: int | None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class EmbeddingRecord:
    """Embedding container."""

    chunk_id: str
    vector: list[float]
    model: str
    dimension: int
    dtype: str


@dataclass(slots=True)
class IndexJobResult:
    """Summary of an indexing operation."""

    indexed_docs: int = 0
    indexed_chunks: int = 0
    updated_docs: int = 0
    deleted_docs: int = 0
    failed_docs: int = 0
    warnings: list[str] = field(default_factory=list)


@dataclass(slots=True)
class JobRecord:
    """Persistent job state."""

    job_id: str
    project_id: str
    job_type: JobType
    status: JobStatus
    trigger_type: str
    started_at: datetime | None = None
    heartbeat_at: datetime | None = None
    finished_at: datetime | None = None
    request_payload: dict[str, Any] = field(default_factory=dict)
    summary_payload: dict[str, Any] = field(default_factory=dict)
    error_payload: dict[str, Any] | None = None


@dataclass(slots=True)
class ProjectLock:
    """Exclusive project lock."""

    project_id: str
    lock_owner: str
    lock_type: LockType
    acquired_at: datetime
    expires_at: datetime


@dataclass(slots=True)
class AnalysisResult:
    """Document analysis output placeholder for later stages."""

    doc_type: str
    language: str | None
    has_headings: bool
    has_code: bool
    recommended_chunking: str
    priority_sections: list[str] = field(default_factory=list)
    entities: list[str] = field(default_factory=list)


@dataclass(slots=True)
class RetrievalHit:
    """Retrieval hit placeholder for later stages."""

    doc_id: str
    chunk_id: str
    score: float
    path: str
    section: str | None = None
    preview: str | None = None


@dataclass(slots=True)
class AnswerResult:
    """RAG answer placeholder for later stages."""

    answer_short: str
    sources: list[dict[str, Any]]
    needs_expansion: bool
    usage: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class ConsolidationPlan:
    """Consolidation execution plan placeholder."""

    project_id: str
    signals: dict[str, Any]
    operations: list[dict[str, Any]] = field(default_factory=list)


@dataclass(slots=True)
class ConsolidationResult:
    """Consolidation result placeholder."""

    project_id: str
    operations_applied: int = 0
    audit_records: int = 0
    warnings: list[str] = field(default_factory=list)
