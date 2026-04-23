from __future__ import annotations

import sqlite3
from pathlib import Path

from pigmeu_never_forget.services.jobs import JobService
from pigmeu_never_forget.services.project import ProjectService
from pigmeu_never_forget.services.workspace import WorkspaceService


def make_workspace_service(workspace_root: Path) -> WorkspaceService:
    settings: dict[str, object] = {
        "workspace": {
            "root_path": str(workspace_root),
            "project_dir_mode": "immediate_children",
            "ignore_dirs": ["_workspace", ".git"],
        },
        "storage": {"collection_prefix": "kb_"},
    }
    return WorkspaceService(settings=settings, project_service=ProjectService(job_service=JobService()))


def test_initialize_workspace_creates_metadata_files(tmp_path: Path) -> None:
    service = make_workspace_service(tmp_path / "workspace")

    result = service.initialize_workspace()

    assert Path(result["metadata_path"]).exists()
    assert Path(result["registry_db_path"]).exists()
    assert (tmp_path / "workspace" / "_workspace" / "config.yaml").exists()
    assert (tmp_path / "workspace" / "_workspace" / "credentials.yaml").exists()


def test_discover_projects_bootstraps_rag_structure(tmp_path: Path) -> None:
    workspace_root = tmp_path / "workspace"
    project_root = workspace_root / "project-a"
    (project_root / "docs").mkdir(parents=True)
    service = make_workspace_service(workspace_root)

    result = service.discover_projects()

    assert result["projects"][0]["project_id"] == "project-a"
    assert (project_root / ".rag" / "project.yaml").exists()
    assert (project_root / ".rag" / "prompts.yaml").exists()
    assert (project_root / ".rag" / "state.db").exists()
    assert (project_root / ".rag" / "memory.db").exists()

    connection = sqlite3.connect(project_root / ".rag" / "state.db")
    tables = {
        row[0]
        for row in connection.execute(
            "select name from sqlite_master where type = 'table'"
        ).fetchall()
    }
    connection.close()
    assert "job_runs" in tables
    assert "project_locks" in tables
