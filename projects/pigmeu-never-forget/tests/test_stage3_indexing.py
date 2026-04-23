from __future__ import annotations

from pathlib import Path

from pigmeu_never_forget.config.loader import build_project_context, build_workspace_paths
from pigmeu_never_forget.domain.models import ProjectContext
from pigmeu_never_forget.services.chunking import ChunkingService
from pigmeu_never_forget.services.embedding import EmbeddingService
from pigmeu_never_forget.services.indexing import IndexingService
from pigmeu_never_forget.services.jobs import JobService
from pigmeu_never_forget.services.project import ProjectService
from pigmeu_never_forget.services.vector_store import VectorStoreService
from pigmeu_never_forget.services.workspace import WorkspaceService
from pigmeu_never_forget.storage.sqlite import sqlite_cursor


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


def build_context(service: WorkspaceService, project_root: Path):
    workspace_paths = build_workspace_paths(service.settings)
    return build_project_context(service.settings, workspace_paths, project_root)


def test_stage3_indexing_pipeline_and_vector_search(tmp_path: Path) -> None:
    workspace_root = tmp_path / "workspace"
    project_root = workspace_root / "project-a"
    docs_dir = project_root / "docs"
    docs_dir.mkdir(parents=True)
    source_file = docs_dir / "auth.md"
    source_file.write_text(
        "# Authentication\nJWT tokens are used.\n\n## Refresh\nRefresh token flow.\n",
        encoding="utf-8",
    )

    workspace = make_workspace_service(workspace_root)
    workspace.discover_projects()
    context = build_context(workspace, project_root)
    indexing = IndexingService()

    first = indexing.index_project(context)
    assert first.failed_docs == 0
    assert first.updated_docs == 1
    assert first.indexed_chunks > 0

    second = indexing.index_project(context)
    assert second.failed_docs == 0
    assert second.updated_docs == 0
    assert second.indexed_chunks == 0

    embedder = EmbeddingService()
    query_vector = embedder.embed_query(context, "refresh token")
    hits = VectorStoreService().search(context, query_vector, top_k=3)
    assert len(hits) >= 1
    assert hits[0].doc_id.startswith("project-a::docs__auth.md")

    source_file.unlink()
    third = indexing.index_project(context)
    assert third.deleted_docs == 1

    with sqlite_cursor(context.state_db_path) as connection:
        row = connection.execute(
            "select status from documents where path = ?",
            ("docs/auth.md",),
        ).fetchone()
    assert row is not None
    assert row["status"] == "deleted"


def test_rename_deactivates_old_document_path(tmp_path: Path) -> None:
    workspace_root = tmp_path / "workspace"
    project_root = workspace_root / "project-a"
    docs_dir = project_root / "docs"
    docs_dir.mkdir(parents=True)
    old_file = docs_dir / "old.md"
    old_file.write_text("# Doc\nsame body\n", encoding="utf-8")

    workspace = make_workspace_service(workspace_root)
    workspace.discover_projects()
    context = build_context(workspace, project_root)
    indexing = IndexingService()

    first = indexing.index_project(context)
    assert first.failed_docs == 0

    new_file = docs_dir / "new.md"
    old_file.rename(new_file)
    second = indexing.index_project(context)
    assert second.failed_docs == 0
    assert second.deleted_docs >= 1

    with sqlite_cursor(context.state_db_path) as connection:
        old_row = connection.execute(
            "select status from documents where path = ?",
            ("docs/old.md",),
        ).fetchone()
        new_row = connection.execute(
            "select status from documents where path = ?",
            ("docs/new.md",),
        ).fetchone()
    assert old_row is not None
    assert old_row["status"] == "deleted"
    assert new_row is not None
    assert new_row["status"] == "active"


class FailingChunkingService(ChunkingService):
    def chunk_document(
        self,
        project: ProjectContext,
        doc_id: str,
        path: str,
        text: str,
        section_hint: str | None = None,
    ):
        if path.endswith("fail.md"):
            raise RuntimeError("synthetic chunking failure")
        return super().chunk_document(project, doc_id, path, text, section_hint)


def test_failed_index_does_not_persist_checkpoint_for_failed_file(tmp_path: Path) -> None:
    workspace_root = tmp_path / "workspace"
    project_root = workspace_root / "project-a"
    docs_dir = project_root / "docs"
    docs_dir.mkdir(parents=True)
    good_file = docs_dir / "ok.md"
    bad_file = docs_dir / "fail.md"
    good_file.write_text("good\n", encoding="utf-8")
    bad_file.write_text("bad\n", encoding="utf-8")

    workspace = make_workspace_service(workspace_root)
    workspace.discover_projects()
    context = build_context(workspace, project_root)

    indexing_fail = IndexingService(chunking=FailingChunkingService())
    failed_run = indexing_fail.index_project(context)
    assert failed_run.failed_docs == 1

    with sqlite_cursor(context.state_db_path) as connection:
        bad_checkpoint = connection.execute(
            "select path from file_checkpoints where path = ?",
            ("docs/fail.md",),
        ).fetchone()
    assert bad_checkpoint is None

    indexing_ok = IndexingService()
    recovered_run = indexing_ok.index_project(context)
    assert recovered_run.failed_docs == 0
    assert recovered_run.updated_docs >= 1

    with sqlite_cursor(context.state_db_path) as connection:
        bad_checkpoint_after = connection.execute(
            "select path from file_checkpoints where path = ?",
            ("docs/fail.md",),
        ).fetchone()
    assert bad_checkpoint_after is not None
