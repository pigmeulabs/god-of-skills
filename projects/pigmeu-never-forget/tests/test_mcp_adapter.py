from __future__ import annotations

import json
from pathlib import Path

from pigmeu_never_forget.mcp.adapter import PNFMCPAdapter
from pigmeu_never_forget.storage.sqlite import sqlite_cursor
from pigmeu_never_forget.utils.yaml_compat import safe_dump


def _write_config(tmp_path: Path) -> Path:
    workspace_root = tmp_path / "workspace"
    config_path = tmp_path / "config.yaml"
    config_path.write_text(
        safe_dump(
            {
                "workspace": {
                    "root_path": str(workspace_root),
                    "project_dir_mode": "immediate_children",
                    "ignore_dirs": ["_workspace", ".git"],
                },
                "storage": {"collection_prefix": "kb_"},
            }
        ),
        encoding="utf-8",
    )
    return config_path


def _seed_project(tmp_path: Path) -> tuple[Path, Path]:
    workspace_root = tmp_path / "workspace"
    project_root = workspace_root / "project-a"
    docs_dir = project_root / "docs"
    docs_dir.mkdir(parents=True)
    (docs_dir / "auth.md").write_text("# Auth\nRefresh token flow.\n", encoding="utf-8")
    return workspace_root, project_root


def test_adapter_tools_and_resources_end_to_end(tmp_path: Path) -> None:
    config_path = _write_config(tmp_path)
    _, project_root = _seed_project(tmp_path)

    adapter = PNFMCPAdapter(config_path=str(config_path))

    projects = adapter.list_projects(request_id="req-list")
    assert projects["status"] == "ok"

    sync = adapter.sync_project("project-a", request_id="req-sync")
    assert sync["status"] == "ok"

    indexed = adapter.index_text(
        project_id="project-a",
        title="inline-1",
        text="JWT and refresh token rotation.",
        request_id="req-index",
    )
    assert indexed["status"] == "ok"
    assert int(indexed["data"]["chunks_created"]) >= 1

    search = adapter.search_project("project-a", "refresh token", request_id="req-search")
    assert search["status"] == "ok"

    ask = adapter.ask_project("project-a", "Como funciona refresh token?", request_id="req-ask")
    assert ask["status"] == "ok"
    assert ask["data"]["answer_short"]

    stats = adapter.get_project_stats("project-a", request_id="req-stats")
    assert stats["status"] == "ok"
    assert "stats" in stats["data"]

    state_db = project_root / ".rag" / "state.db"
    with sqlite_cursor(state_db) as connection:
        row = connection.execute(
            "select job_id from job_runs where project_id = ? order by rowid desc limit 1",
            ("project-a",),
        ).fetchone()
        assert row is not None
        job_id = str(row["job_id"])

    job = adapter.get_job_status("project-a", job_id, request_id="req-job")
    assert job["status"] == "ok"
    assert job["data"]["job"]["job_id"] == job_id

    projects_resource = json.loads(adapter.resource_projects())
    assert projects_resource["status"] == "ok"
    summary_resource = json.loads(adapter.resource_project_summary("project-a"))
    assert summary_resource["status"] in {"ok", "error"}
    stats_resource = json.loads(adapter.resource_project_stats("project-a"))
    assert stats_resource["status"] == "ok"
    job_resource = json.loads(adapter.resource_project_job("project-a", job_id))
    assert job_resource["status"] == "ok"

    with sqlite_cursor(state_db) as connection:
        log_count = connection.execute(
            "select count(*) as total from log_events where service = 'mcp' and trace_id = ?",
            ("req-sync",),
        ).fetchone()["total"]
    assert int(log_count) >= 1

