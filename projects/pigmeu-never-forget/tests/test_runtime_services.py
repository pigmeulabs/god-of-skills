from __future__ import annotations

from pathlib import Path

from pigmeu_never_forget.app import create_application
from pigmeu_never_forget.config.loader import build_project_context, build_workspace_paths
from pigmeu_never_forget.services.embedding import EmbeddingService
from pigmeu_never_forget.services.vector_store import VectorStoreService
from pigmeu_never_forget.storage.sqlite import sqlite_cursor
from pigmeu_never_forget.utils.yaml_compat import safe_dump


def test_workspace_runtime_sync_search_ask_stats_and_consolidate(tmp_path: Path) -> None:
    workspace_root = tmp_path / "workspace"
    project_root = workspace_root / "project-a"
    docs_dir = project_root / "docs"
    docs_dir.mkdir(parents=True)
    (docs_dir / "auth.md").write_text(
        "# Auth\nJWT is used.\n\n## Refresh\nRefresh token flow with session rules.\n",
        encoding="utf-8",
    )

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

    app = create_application(str(config_path))
    app.initialize_workspace()
    app.discover_projects()

    sync = app.sync_project("project-a")
    assert sync["status"] == "ok"
    assert sync["result"]["failed_docs"] == 0
    assert sync["result"]["indexed_docs"] >= 1

    search = app.search_project("project-a", "refresh token", top_k=5)
    assert len(search["hits"]) >= 1

    ask = app.ask_project("project-a", "Como funciona refresh token?", top_k=5)
    assert ask["answer_short"]
    assert len(ask["sources"]) >= 1

    stats = app.get_project_stats("project-a")
    assert stats["project_id"] == "project-a"
    assert stats["documents_active"] >= 1
    assert stats["queries_total"] >= 1

    consolidate = app.consolidate_project("project-a")
    assert consolidate["operations_applied"] >= 1


def test_workspace_index_text_and_search_inline(tmp_path: Path) -> None:
    workspace_root = tmp_path / "workspace"
    project_root = workspace_root / "project-a"
    docs_dir = project_root / "docs"
    docs_dir.mkdir(parents=True)
    (docs_dir / "seed.md").write_text("# Seed\nbaseline", encoding="utf-8")

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
    app = create_application(str(config_path))
    app.initialize_workspace()
    app.discover_projects()
    app.sync_project("project-a")

    indexed = app.index_text(
        "project-a",
        title="auth-notes",
        text="Refresh token lifecycle and JWT rotation policies.",
        source_type="inline_text",
        tags=["manual"],
    )
    assert indexed["doc_id"].startswith("project-a::")
    assert int(indexed["chunks_created"]) >= 1

    hits = app.search_project("project-a", "refresh token lifecycle", top_k=5)
    assert len(hits["hits"]) >= 1


def test_vector_store_top_k_zero_returns_empty(tmp_path: Path) -> None:
    workspace_root = tmp_path / "workspace"
    project_root = workspace_root / "project-a"
    docs_dir = project_root / "docs"
    docs_dir.mkdir(parents=True)
    (docs_dir / "a.md").write_text("A content", encoding="utf-8")

    config_path = tmp_path / "config.yaml"
    config_path.write_text(
        safe_dump(
            {
                "workspace": {
                    "root_path": str(workspace_root),
                    "project_dir_mode": "immediate_children",
                    "ignore_dirs": ["_workspace", ".git"],
                }
            }
        ),
        encoding="utf-8",
    )
    app = create_application(str(config_path))
    app.initialize_workspace()
    app.discover_projects()
    app.sync_project("project-a")

    workspace_paths = build_workspace_paths(app.settings)
    context = build_project_context(app.settings, workspace_paths, project_root)
    query_vector = EmbeddingService().embed_query(context, "a")
    hits = VectorStoreService().search(context, query_vector, top_k=0)
    assert hits == []
