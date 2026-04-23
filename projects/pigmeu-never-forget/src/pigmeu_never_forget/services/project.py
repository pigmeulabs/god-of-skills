"""Project bootstrap and inspection services."""

from __future__ import annotations

from pathlib import Path

from pigmeu_never_forget.config.defaults import copy_project_defaults, copy_prompt_defaults
from pigmeu_never_forget.config.loader import build_project_context, build_workspace_paths
from pigmeu_never_forget.domain.errors import AppError
from pigmeu_never_forget.domain.enums import ErrorCode, JobStatus, JobType, LockType
from pigmeu_never_forget.domain.models import ProjectContext
from pigmeu_never_forget.services.jobs import JobService
from pigmeu_never_forget.storage.migrations import MEMORY_MIGRATIONS, STATE_MIGRATIONS, apply_migrations
from pigmeu_never_forget.utils.paths import ensure_absolute_path
from pigmeu_never_forget.utils.yaml_compat import safe_dump


class ProjectService:
    """Manage project bootstrap and local persistence."""

    def __init__(self, job_service: JobService) -> None:
        self._job_service = job_service

    def initialize_project(
        self,
        workspace_settings: dict[str, object],
        project_root: Path,
    ) -> dict[str, object]:
        """Create the local `.rag` structure and bootstrap SQLite schemas."""
        project_root = ensure_absolute_path(project_root)
        if not project_root.exists() or not project_root.is_dir():
            raise AppError(
                code=ErrorCode.PROJECT_NOT_FOUND,
                message=f"Project path not found: {project_root}",
                details={"project_path": str(project_root)},
            )

        workspace_paths = build_workspace_paths(workspace_settings)
        context = build_project_context(workspace_settings, workspace_paths, project_root)
        self._ensure_rag_structure(context)
        self._write_default_configs(context)
        state_result = apply_migrations(context.state_db_path, STATE_MIGRATIONS)
        memory_result = apply_migrations(context.memory_db_path, MEMORY_MIGRATIONS)

        job = self._job_service.create_job(
            db_path=context.state_db_path,
            project_id=context.project_id,
            job_type=JobType.DISCOVER,
            trigger_type="bootstrap",
            request_payload={"project_path": str(project_root)},
        )
        self._job_service.mark_running(context.state_db_path, job.job_id)
        self._job_service.acquire_lock(
            db_path=context.state_db_path,
            project_id=context.project_id,
            lock_type=LockType.SYNC,
            lock_owner=job.job_id,
        )
        self._job_service.finish_job(
            db_path=context.state_db_path,
            job_id=job.job_id,
            status=JobStatus.SUCCEEDED,
            summary_payload={
                "state_migrations": state_result.applied_versions,
                "memory_migrations": memory_result.applied_versions,
            },
        )
        self._job_service.release_lock(
            db_path=context.state_db_path,
            project_id=context.project_id,
            lock_owner=job.job_id,
        )
        return self.describe_project(context)

    def describe_project(self, context: ProjectContext) -> dict[str, object]:
        """Return a JSON-serializable project description."""
        return {
            "project_id": context.project_id,
            "project_name": context.project_name,
            "root_path": str(context.root_path),
            "rag_path": str(context.rag_path),
            "state_db_path": str(context.state_db_path),
            "memory_db_path": str(context.memory_db_path),
            "qdrant_collection": context.qdrant_collection,
        }

    def _ensure_rag_structure(self, context: ProjectContext) -> None:
        for path in (context.rag_path, context.faiss_dir, context.cache_dir, context.logs_dir):
            path.mkdir(parents=True, exist_ok=True)

    def _write_default_configs(self, context: ProjectContext) -> None:
        if not context.project_config_path.exists():
            defaults = copy_project_defaults()
            defaults["project"]["name"] = context.project_name
            with context.project_config_path.open("w", encoding="utf-8") as handle:
                handle.write(safe_dump(defaults, sort_keys=False))
        if not context.prompts_config_path.exists():
            with context.prompts_config_path.open("w", encoding="utf-8") as handle:
                handle.write(safe_dump(copy_prompt_defaults(), sort_keys=False))
