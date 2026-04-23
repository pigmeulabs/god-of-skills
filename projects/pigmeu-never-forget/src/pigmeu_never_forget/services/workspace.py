"""Workspace discovery and bootstrap services."""

from __future__ import annotations

import json
from pathlib import Path

from pigmeu_never_forget.config.defaults import copy_workspace_defaults
from pigmeu_never_forget.config.loader import build_project_context, build_workspace_paths
from pigmeu_never_forget.services.answering import AnswerService
from pigmeu_never_forget.services.indexing import IndexingService
from pigmeu_never_forget.services.memory import MemoryConsolidationService
from pigmeu_never_forget.services.project import ProjectService
from pigmeu_never_forget.services.retrieval import RetrievalService
from pigmeu_never_forget.storage.registry import RegistryStore
from pigmeu_never_forget.storage.sqlite import sqlite_cursor
from pigmeu_never_forget.utils.paths import ensure_absolute_path
from pigmeu_never_forget.utils.yaml_compat import safe_dump


class WorkspaceService:
    """High-level workspace orchestration service."""

    def __init__(
        self,
        settings: dict[str, object],
        project_service: ProjectService,
        indexing_service: IndexingService | None = None,
        retrieval_service: RetrievalService | None = None,
        answer_service: AnswerService | None = None,
        memory_consolidation_service: MemoryConsolidationService | None = None,
    ) -> None:
        self._settings = settings
        self._project_service = project_service
        self._indexing_service = indexing_service or IndexingService()
        self._retrieval_service = retrieval_service or RetrievalService()
        self._answer_service = answer_service or AnswerService()
        self._memory_consolidation_service = memory_consolidation_service or MemoryConsolidationService()
        self._paths = build_workspace_paths(settings)
        self._registry = RegistryStore(self._paths.registry_db_path)

    @property
    def settings(self) -> dict[str, object]:
        """Expose workspace settings."""
        return self._settings

    def initialize_workspace(self) -> dict[str, object]:
        """Create metadata directories and registry."""
        self._paths.root_path.mkdir(parents=True, exist_ok=True)
        self._paths.metadata_path.mkdir(parents=True, exist_ok=True)
        self._paths.logs_path.mkdir(parents=True, exist_ok=True)
        if not self._paths.config_path.exists():
            with self._paths.config_path.open("w", encoding="utf-8") as handle:
                handle.write(safe_dump(copy_workspace_defaults(), sort_keys=False))
        if not self._paths.credentials_path.exists():
            with self._paths.credentials_path.open("w", encoding="utf-8") as handle:
                handle.write(safe_dump({}, sort_keys=False))
        self._registry.initialize()
        return {
            "workspace_root": str(self._paths.root_path),
            "metadata_path": str(self._paths.metadata_path),
            "registry_db_path": str(self._paths.registry_db_path),
        }

    def discover_projects(self) -> dict[str, object]:
        """Discover immediate child projects and bootstrap missing `.rag` folders."""
        self.initialize_workspace()
        ignore_dirs = set(self._settings["workspace"]["ignore_dirs"])
        projects: list[dict[str, object]] = []
        for child in sorted(self._paths.root_path.iterdir()):
            if not child.is_dir() or child.name in ignore_dirs:
                continue
            description = self.initialize_project(child)
            projects.append(description)
            record = self._registry.build_record(
                project_id=str(description["project_id"]),
                project_name=str(description["project_name"]),
                root_path=str(description["root_path"]),
                status="ready",
            )
            self._registry.upsert_project(record)
        return {"projects": projects}

    def initialize_project(self, project_path: Path) -> dict[str, object]:
        """Bootstrap a single project path."""
        project_path = ensure_absolute_path(project_path, self._paths.root_path)
        return self._project_service.initialize_project(self._settings, project_path)

    def build_context(self, project_path: Path) -> dict[str, object]:
        """Build a project context for inspection."""
        context = build_project_context(self._settings, self._paths, ensure_absolute_path(project_path))
        return self._project_service.describe_project(context)

    def sync_project(self, project_id: str) -> dict[str, object]:
        """Run incremental indexing for one project."""
        context = self._resolve_project_context(project_id)
        result = self._indexing_service.index_project(context)
        return {
            "project_id": project_id,
            "status": "ok",
            "result": {
                "indexed_docs": result.indexed_docs,
                "indexed_chunks": result.indexed_chunks,
                "updated_docs": result.updated_docs,
                "deleted_docs": result.deleted_docs,
                "failed_docs": result.failed_docs,
                "warnings": result.warnings,
            },
        }

    def search_project(self, project_id: str, query: str, top_k: int = 8) -> dict[str, object]:
        """Run retrieval search."""
        context = self._resolve_project_context(project_id)
        hits = self._retrieval_service.search(context, query, top_k=top_k)
        return {
            "project_id": project_id,
            "hits": [
                {
                    "doc_id": hit.doc_id,
                    "chunk_id": hit.chunk_id,
                    "score": hit.score,
                    "path": hit.path,
                    "section": hit.section,
                    "preview": hit.preview,
                }
                for hit in hits
            ],
        }

    def index_text(
        self,
        project_id: str,
        title: str,
        text: str,
        source_type: str = "inline_text",
        tags: list[str] | None = None,
    ) -> dict[str, object]:
        """Index inline text payload into project knowledge base."""
        context = self._resolve_project_context(project_id)
        result = self._indexing_service.index_text(
            project=context,
            title=title,
            text=text,
            source_type=source_type,
            tags=tags or [],
        )
        return {"project_id": project_id, **result}

    def ask_project(self, project_id: str, question: str, top_k: int = 6) -> dict[str, object]:
        """Run retrieval + answer composition."""
        context = self._resolve_project_context(project_id)
        answer = self._answer_service.answer_from_question(
            project=context,
            question=question,
            top_k=top_k,
            retrieval=self._retrieval_service,
        )
        return {
            "project_id": project_id,
            "answer_short": answer.answer_short,
            "sources": answer.sources,
            "needs_expansion": answer.needs_expansion,
            "usage": answer.usage,
        }

    def consolidate_project(self, project_id: str) -> dict[str, object]:
        """Run incremental memory consolidation."""
        context = self._resolve_project_context(project_id)
        plan = self._memory_consolidation_service.build_plan(context, signals={})
        result = self._memory_consolidation_service.execute(context, plan)
        return {
            "project_id": project_id,
            "operations_applied": result.operations_applied,
            "audit_records": result.audit_records,
            "warnings": result.warnings,
        }

    def get_project_stats(self, project_id: str) -> dict[str, object]:
        """Return basic project stats."""
        context = self._resolve_project_context(project_id)
        return self._retrieval_service.get_project_stats(context)

    def get_job_status(self, project_id: str, job_id: str) -> dict[str, object]:
        """Return a single job status payload for a project."""
        context = self._resolve_project_context(project_id)
        with sqlite_cursor(context.state_db_path) as connection:
            row = connection.execute(
                """
                select job_id, project_id, job_type, status, started_at, heartbeat_at, finished_at,
                       trigger_type, request_json, summary_json, error_json
                from job_runs
                where project_id = ? and job_id = ?
                """,
                (project_id, job_id),
            ).fetchone()
        if row is None:
            raise FileNotFoundError(f"Job not found for project: {project_id}, job_id: {job_id}")
        return {
            "job_id": str(row["job_id"]),
            "project_id": str(row["project_id"]),
            "job_type": str(row["job_type"]),
            "status": str(row["status"]),
            "started_at": row["started_at"],
            "heartbeat_at": row["heartbeat_at"],
            "finished_at": row["finished_at"],
            "trigger_type": str(row["trigger_type"]),
            "request": json.loads(str(row["request_json"] or "{}")),
            "summary": json.loads(str(row["summary_json"] or "{}")),
            "error": json.loads(str(row["error_json"])) if row["error_json"] else None,
        }

    def _resolve_project_context(self, project_id: str):
        self.initialize_workspace()
        for child in sorted(self._paths.root_path.iterdir()):
            if not child.is_dir() or child.name in set(self._settings["workspace"]["ignore_dirs"]):
                continue
            context = build_project_context(self._settings, self._paths, child)
            if context.project_id == project_id or child.name == project_id:
                return context
        raise FileNotFoundError(f"Project not found: {project_id}")
