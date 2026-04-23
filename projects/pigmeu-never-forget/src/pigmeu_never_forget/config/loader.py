"""Configuration loading and validation."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from pigmeu_never_forget.config.defaults import (
    copy_project_defaults,
    copy_prompt_defaults,
    copy_workspace_defaults,
)
from pigmeu_never_forget.domain.errors import AppError
from pigmeu_never_forget.domain.enums import ErrorCode
from pigmeu_never_forget.domain.models import ProjectContext, WorkspacePaths
from pigmeu_never_forget.utils.merge import deep_merge
from pigmeu_never_forget.utils.paths import ensure_absolute_path, slugify
from pigmeu_never_forget.utils.yaml_compat import safe_load


def load_yaml_file(path: Path) -> dict[str, Any]:
    """Load a YAML file into a dictionary."""
    try:
        with path.open("r", encoding="utf-8") as handle:
            payload = safe_load(handle.read()) or {}
    except FileNotFoundError as exc:
        raise AppError(
            code=ErrorCode.INVALID_REQUEST,
            message=f"Configuration file not found: {path}",
            details={"path": str(path)},
        ) from exc
    if not isinstance(payload, dict):
        raise AppError(
            code=ErrorCode.INVALID_REQUEST,
            message=f"Configuration file must contain a mapping: {path}",
            details={"path": str(path)},
        )
    return payload


def load_workspace_settings(config_path: str | None = None) -> dict[str, Any]:
    """Load workspace settings merged with defaults."""
    defaults = copy_workspace_defaults()
    if config_path is None:
        return defaults

    path = ensure_absolute_path(Path(config_path))
    payload = load_yaml_file(path)
    return deep_merge(defaults, payload)


def build_workspace_paths(settings: dict[str, Any], base_dir: Path | None = None) -> WorkspacePaths:
    """Resolve workspace paths from settings."""
    base = ensure_absolute_path(base_dir or Path.cwd())
    workspace_root = ensure_absolute_path(Path(str(settings["workspace"]["root_path"])), base)
    metadata_path = workspace_root / "_workspace"
    return WorkspacePaths(
        root_path=workspace_root,
        metadata_path=metadata_path,
        config_path=metadata_path / "config.yaml",
        credentials_path=metadata_path / "credentials.yaml",
        registry_db_path=metadata_path / "registry.db",
        logs_path=metadata_path / "logs",
    )


def load_project_settings(project_config_path: Path | None = None) -> dict[str, Any]:
    """Load project settings merged with defaults."""
    defaults = copy_project_defaults()
    if project_config_path is None or not project_config_path.exists():
        return defaults
    payload = load_yaml_file(project_config_path)
    return deep_merge(defaults, payload)


def load_prompt_settings(prompts_config_path: Path | None = None) -> dict[str, Any]:
    """Load prompt settings merged with defaults."""
    defaults = copy_prompt_defaults()
    if prompts_config_path is None or not prompts_config_path.exists():
        return defaults
    payload = load_yaml_file(prompts_config_path)
    return deep_merge(defaults, payload)


def build_project_context(
    workspace_settings: dict[str, Any],
    workspace_paths: WorkspacePaths,
    project_root: Path,
) -> ProjectContext:
    """Build a project context from a project root path."""
    project_root = ensure_absolute_path(project_root)
    rag_path = project_root / ".rag"
    project_config_path = rag_path / "project.yaml"
    prompts_config_path = rag_path / "prompts.yaml"
    project_settings = load_project_settings(project_config_path)
    project_name = str(project_settings["project"].get("name") or project_root.name)
    collection_prefix = str(workspace_settings["storage"]["collection_prefix"])
    project_slug = slugify(project_root.name)
    settings = deep_merge(workspace_settings, {"project_settings": project_settings})
    return ProjectContext(
        project_id=project_slug,
        project_name=project_name,
        root_path=project_root,
        rag_path=rag_path,
        project_config_path=project_config_path,
        prompts_config_path=prompts_config_path,
        state_db_path=rag_path / "state.db",
        memory_db_path=rag_path / "memory.db",
        faiss_dir=rag_path / "faiss",
        cache_dir=rag_path / "cache",
        logs_dir=rag_path / "logs",
        qdrant_collection=f"{collection_prefix}{project_slug}",
        settings=settings,
    )
