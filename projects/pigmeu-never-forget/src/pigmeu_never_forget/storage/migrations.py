"""Forward-only SQLite schema bootstrap."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from pigmeu_never_forget.storage.sqlite import sqlite_cursor

STATE_MIGRATIONS: list[str] = [
    """
    create table if not exists schema_migrations (
      version integer primary key,
      applied_at text not null
    );
    """,
    """
    create table if not exists documents (
      doc_id text primary key,
      project_id text not null,
      path text not null,
      source_type text not null,
      title text,
      mime_type text,
      source_hash text not null,
      content_hash text not null,
      parser_version text not null,
      status text not null check (status in ('active', 'deleted', 'error')),
      last_seen_at text not null,
      last_indexed_at text,
      last_error text,
      summary_short text,
      summary_full text,
      topics_json text not null default '[]',
      metadata_json text not null default '{}',
      unique(project_id, path)
    );
    create index if not exists idx_documents_path on documents(project_id, path);
    create index if not exists idx_documents_content_hash on documents(project_id, content_hash);
    """,
    """
    create table if not exists chunks (
      chunk_id text primary key,
      doc_id text not null references documents(doc_id) on delete cascade,
      chunk_hash text not null,
      position integer not null,
      section text,
      token_count integer,
      text_preview text not null,
      body_ref text,
      summary_short text,
      embedding_model text not null,
      embedding_dim integer not null,
      qdrant_point_id text not null default '',
      faiss_id integer,
      active integer not null default 1 check (active in (0, 1)),
      metadata_json text not null default '{}',
      unique(doc_id, position),
      unique(doc_id, chunk_hash)
    );
    create index if not exists idx_chunks_doc_active on chunks(doc_id, active);
    create index if not exists idx_chunks_qdrant on chunks(qdrant_point_id);
    """,
    """
    create table if not exists document_bodies (
      doc_id text primary key references documents(doc_id) on delete cascade,
      normalized_text text not null
    );
    """,
    """
    create table if not exists job_runs (
      job_id text primary key,
      project_id text not null,
      job_type text not null check (job_type in ('discover', 'sync', 'index', 'query', 'consolidate')),
      status text not null check (status in ('queued', 'running', 'succeeded', 'failed', 'cancelled')),
      started_at text,
      heartbeat_at text,
      finished_at text,
      trigger_type text not null,
      request_json text not null default '{}',
      summary_json text not null default '{}',
      error_json text
    );
    create index if not exists idx_job_runs_project_status on job_runs(project_id, status);
    """,
    """
    create table if not exists api_calls (
      call_id text primary key,
      project_id text not null,
      job_id text references job_runs(job_id),
      provider text not null,
      model text not null,
      api_key_name text,
      operation text not null,
      duration_ms integer not null,
      success integer not null check (success in (0, 1)),
      http_status integer,
      retry_count integer not null default 0,
      input_tokens_est integer,
      output_tokens_est integer,
      prompt_template_name text,
      prompt_template_version text,
      input_hash text,
      response_hash text,
      created_at text not null
    );
    """,
    """
    create table if not exists log_events (
      event_id text primary key,
      project_id text not null,
      job_id text references job_runs(job_id),
      timestamp text not null,
      level text not null,
      service text not null,
      event_type text not null,
      trace_id text,
      payload_json text not null default '{}'
    );
    create index if not exists idx_log_events_project_time on log_events(project_id, timestamp);
    """,
    """
    create table if not exists file_checkpoints (
      path text primary key,
      project_id text not null,
      source_hash text not null,
      content_hash text not null,
      parser_version text not null,
      last_scan_at text not null
    );
    """,
    """
    create table if not exists project_locks (
      project_id text primary key,
      lock_owner text not null,
      lock_type text not null check (lock_type in ('sync', 'consolidate')),
      acquired_at text not null,
      expires_at text not null
    );
    """,
]

MEMORY_MIGRATIONS: list[str] = [
    """
    create table if not exists schema_migrations (
      version integer primary key,
      applied_at text not null
    );
    """,
    """
    create table if not exists memory_facts (
      fact_id text primary key,
      project_id text not null,
      fact_text text not null,
      scope text not null check (scope in ('document', 'project', 'query')),
      confidence real not null check (confidence >= 0 and confidence <= 1),
      status text not null check (status in ('active', 'superseded', 'discarded')),
      source_ref text not null,
      evidence_json text not null default '[]',
      created_at text not null,
      updated_at text not null,
      superseded_by text references memory_facts(fact_id)
    );
    create index if not exists idx_memory_facts_project_status on memory_facts(project_id, status);
    """,
    """
    create table if not exists project_summary (
      project_id text primary key,
      version integer not null,
      summary_short text not null,
      summary_full text not null,
      active_facts_compact_json text not null default '[]',
      updated_at text not null
    );
    """,
    """
    create table if not exists entities (
      entity_id text primary key,
      project_id text not null,
      name text not null,
      type text not null,
      description text,
      canonical integer not null default 1 check (canonical in (0, 1)),
      created_at text not null,
      updated_at text not null,
      unique(project_id, name, type)
    );
    """,
    """
    create table if not exists entity_aliases (
      alias_id text primary key,
      entity_id text not null references entities(entity_id) on delete cascade,
      alias text not null,
      confidence real not null check (confidence >= 0 and confidence <= 1),
      source_ref text not null,
      unique(entity_id, alias)
    );
    """,
    """
    create table if not exists entity_links (
      link_id text primary key,
      source_entity_id text not null references entities(entity_id) on delete cascade,
      relation text not null,
      target_entity_id text not null references entities(entity_id) on delete cascade,
      confidence real not null check (confidence >= 0 and confidence <= 1),
      source_ref text not null,
      unique(source_entity_id, relation, target_entity_id)
    );
    """,
    """
    create table if not exists query_history (
      query_id text primary key,
      project_id text not null,
      query_text text not null,
      rewritten_query text,
      response_summary text,
      sources_json text not null default '[]',
      latency_ms integer not null,
      created_at text not null
    );
    """,
    """
    create table if not exists consolidation_audit (
      audit_id text primary key,
      project_id text not null,
      job_id text,
      operation text not null check (operation in ('prune', 'merge', 'refresh', 'rebuild')),
      target_type text not null,
      target_id text not null,
      before_json text,
      after_json text,
      reason text not null,
      confidence real,
      model text,
      created_at text not null
    );
    create index if not exists idx_consolidation_audit_project_time on consolidation_audit(project_id, created_at);
    """,
]


@dataclass(slots=True)
class MigrationResult:
    """Summary of applied migrations."""

    db_path: Path
    applied_versions: list[int]


def apply_migrations(db_path: Path, migrations: list[str]) -> MigrationResult:
    """Apply forward-only migrations to a SQLite database."""
    applied_versions: list[int] = []
    with sqlite_cursor(db_path) as connection:
        connection.execute(
            "create table if not exists schema_migrations (version integer primary key, applied_at text not null)"
        )
        existing = {
            row["version"]
            for row in connection.execute("select version from schema_migrations").fetchall()
        }
        for version, statement in enumerate(migrations, start=1):
            if version in existing:
                continue
            connection.executescript(statement)
            connection.execute(
                "insert into schema_migrations(version, applied_at) values (?, datetime('now'))",
                (version,),
            )
            applied_versions.append(version)
    return MigrationResult(db_path=db_path, applied_versions=applied_versions)
