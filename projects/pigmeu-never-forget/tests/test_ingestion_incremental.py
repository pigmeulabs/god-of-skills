from __future__ import annotations

from pathlib import Path

from pigmeu_never_forget.config.loader import build_project_context, build_workspace_paths
from pigmeu_never_forget.services.ingestion import IngestionService
from pigmeu_never_forget.services.jobs import JobService
from pigmeu_never_forget.services.project import ProjectService
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


def test_incremental_diff_detects_unchanged_after_persist(tmp_path: Path) -> None:
    workspace_root = tmp_path / "workspace"
    project_root = workspace_root / "project-a"
    docs_dir = project_root / "docs"
    docs_dir.mkdir(parents=True)
    (docs_dir / "guide.md").write_text("# Guide\nsame content\n", encoding="utf-8")

    workspace = make_workspace_service(workspace_root)
    workspace.discover_projects()
    context = build_context(workspace, project_root)
    ingestion = IngestionService()

    snapshots_first = ingestion.build_snapshots(context)
    first_diff = ingestion.diff_snapshots(context, snapshots_first)
    assert first_diff.to_summary() == {
        "new": 1,
        "modified": 0,
        "unchanged": 0,
        "deleted": 0,
        "renamed": 0,
    }

    ingestion.persist_checkpoints(context, snapshots_first, first_diff)
    snapshots_second = ingestion.build_snapshots(context)
    second_diff = ingestion.diff_snapshots(context, snapshots_second)
    assert second_diff.to_summary() == {
        "new": 0,
        "modified": 0,
        "unchanged": 1,
        "deleted": 0,
        "renamed": 0,
    }


def test_incremental_diff_detects_rename_without_delete_and_new(tmp_path: Path) -> None:
    workspace_root = tmp_path / "workspace"
    project_root = workspace_root / "project-a"
    docs_dir = project_root / "docs"
    docs_dir.mkdir(parents=True)
    old_file = docs_dir / "old-name.md"
    old_file.write_text("same body\n", encoding="utf-8")

    workspace = make_workspace_service(workspace_root)
    workspace.discover_projects()
    context = build_context(workspace, project_root)
    ingestion = IngestionService()

    initial_snapshots = ingestion.build_snapshots(context)
    initial_diff = ingestion.diff_snapshots(context, initial_snapshots)
    ingestion.persist_checkpoints(context, initial_snapshots, initial_diff)

    new_file = docs_dir / "new-name.md"
    old_file.rename(new_file)
    rename_snapshots = ingestion.build_snapshots(context)
    rename_diff = ingestion.diff_snapshots(context, rename_snapshots)
    assert rename_diff.to_summary() == {
        "new": 0,
        "modified": 0,
        "unchanged": 0,
        "deleted": 0,
        "renamed": 1,
    }

    ingestion.persist_checkpoints(context, rename_snapshots, rename_diff)
    after_rename = ingestion.diff_snapshots(context, ingestion.build_snapshots(context))
    assert after_rename.to_summary() == {
        "new": 0,
        "modified": 0,
        "unchanged": 1,
        "deleted": 0,
        "renamed": 0,
    }


def test_incremental_diff_detects_deletion(tmp_path: Path) -> None:
    workspace_root = tmp_path / "workspace"
    project_root = workspace_root / "project-a"
    docs_dir = project_root / "docs"
    docs_dir.mkdir(parents=True)
    keep_file = docs_dir / "keep.md"
    remove_file = docs_dir / "remove.md"
    keep_file.write_text("keep\n", encoding="utf-8")
    remove_file.write_text("remove\n", encoding="utf-8")

    workspace = make_workspace_service(workspace_root)
    workspace.discover_projects()
    context = build_context(workspace, project_root)
    ingestion = IngestionService()

    first = ingestion.build_snapshots(context)
    first_diff = ingestion.diff_snapshots(context, first)
    ingestion.persist_checkpoints(context, first, first_diff)

    remove_file.unlink()
    second = ingestion.build_snapshots(context)
    second_diff = ingestion.diff_snapshots(context, second)
    assert second_diff.to_summary() == {
        "new": 0,
        "modified": 0,
        "unchanged": 1,
        "deleted": 1,
        "renamed": 0,
    }


def test_pending_vector_reconciliation_roundtrip(tmp_path: Path) -> None:
    workspace_root = tmp_path / "workspace"
    project_root = workspace_root / "project-a"
    (project_root / "docs").mkdir(parents=True)

    workspace = make_workspace_service(workspace_root)
    workspace.discover_projects()
    context = build_context(workspace, project_root)
    ingestion = IngestionService()

    with sqlite_cursor(context.state_db_path) as connection:
        connection.execute(
            """
            insert into documents(
              doc_id, project_id, path, source_type, title, mime_type, source_hash, content_hash,
              parser_version, status, last_seen_at, metadata_json, topics_json
            ) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), '{}', '[]')
            """,
            (
                "doc_1",
                context.project_id,
                "docs/a.md",
                "file",
                "a",
                "text/markdown",
                "shash",
                "chash",
                "v1",
                "active",
            ),
        )
        connection.execute(
            """
            insert into chunks(
              chunk_id, doc_id, chunk_hash, position, text_preview, embedding_model, embedding_dim, qdrant_point_id, active, metadata_json
            ) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            ("chunk_1", "doc_1", "chunk_hash", 0, "preview", "mistral-embed", 1024, "", 1, "{}"),
        )

    pending_before = ingestion.list_pending_vector_reconciliation(context)
    assert pending_before == ["chunk_1"]

    ingestion.mark_chunk_vector_confirmed(context, "chunk_1", "qdrant-point-1")
    pending_after = ingestion.list_pending_vector_reconciliation(context)
    assert pending_after == []


def test_normalization_produces_markdown_for_html_json_csv_and_binary_stubs(tmp_path: Path) -> None:
    workspace_root = tmp_path / "workspace"
    project_root = workspace_root / "project-a"
    docs_dir = project_root / "docs"
    docs_dir.mkdir(parents=True)

    html_file = docs_dir / "page.html"
    html_file.write_text("<h1>Titulo</h1><p>Corpo <b>forte</b></p>", encoding="utf-8")
    json_file = docs_dir / "data.json"
    json_file.write_text('{"k":"v","n":1}', encoding="utf-8")
    csv_file = docs_dir / "table.csv"
    csv_file.write_text("c1,c2\nv1,v2\n", encoding="utf-8")
    img_file = docs_dir / "diagram.png"
    img_file.write_bytes(b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR")
    pdf_file = docs_dir / "manual.pdf"
    pdf_file.write_bytes(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")

    workspace = make_workspace_service(workspace_root)
    workspace.discover_projects()
    context = build_context(workspace, project_root)
    ingestion = IngestionService()

    html_doc = ingestion.normalize_file(context, html_file)
    json_doc = ingestion.normalize_file(context, json_file)
    csv_doc = ingestion.normalize_file(context, csv_file)
    img_doc = ingestion.normalize_file(context, img_file)
    pdf_doc = ingestion.normalize_file(context, pdf_file)

    assert "Titulo" in html_doc.raw_text
    assert "Corpo" in html_doc.raw_text
    assert "JSON" in json_doc.raw_text
    assert "k" in json_doc.raw_text
    assert "CSV" in csv_doc.raw_text
    assert "c1" in csv_doc.raw_text
    assert "IMAGE Document" in img_doc.raw_text
    assert "diagram.png" in img_doc.raw_text
    assert "PDF Document" in pdf_doc.raw_text
    assert "manual.pdf" in pdf_doc.raw_text
