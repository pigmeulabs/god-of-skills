"""Default configuration payloads used during bootstrap."""

from __future__ import annotations

from copy import deepcopy

WORKSPACE_DEFAULTS: dict[str, object] = {
    "workspace": {
        "root_path": ".",
        "project_dir_mode": "immediate_children",
        "ignore_dirs": [
            "_workspace",
            ".git",
            ".idea",
            "node_modules",
            "__pycache__",
            ".venv",
        ],
    },
    "providers": {
        "llm_provider": "mistral",
        "embedding_provider": "mistral",
        "fallback_llm_provider": "groq",
    },
    "models": {
        "analysis_model": "mistral-small-latest",
        "answer_model": "mistral-small-latest",
        "embedding_model_text": "mistral-embed",
        "embedding_model_code": "codestral-embed",
        "fast_structured_model": "groq-structured-default",
    },
    "chunking": {
        "mode": "hybrid",
        "chunk_size_chars": 1600,
        "overlap_chars": 220,
        "min_chunk_chars": 300,
        "respect_headers": True,
        "split_code_blocks": True,
    },
    "retrieval": {
        "top_k": 8,
        "max_context_chunks": 6,
        "score_threshold": 0.35,
        "use_summary_first": True,
        "context_budget_tokens": 2400,
    },
    "storage": {
        "vector_backend": "qdrant",
        "qdrant_url": "http://qdrant:6333",
        "collection_prefix": "kb_",
        "enable_faiss_mirror": True,
    },
    "indexing": {
        "embedding_batch_size": 64,
        "max_retries": 5,
        "backoff_seconds": 2,
        "incremental_mode": True,
        "delete_missing": True,
    },
    "consolidation": {
        "enabled": True,
        "post_sync": True,
        "daily_schedule": False,
        "min_recent_events_for_run": 10,
    },
    "logging": {
        "level": "INFO",
        "json": True,
        "sample_full_prompts": False,
        "persist_api_calls": True,
    },
    "opencode": {
        "optimize_tokens": True,
        "compact_project_summary_tokens": 500,
        "max_active_facts": 20,
        "retrieval_budget_tokens": 1600,
    },
    "session_memory": {
        "enabled": True,
        "root_path": "docs/memories/sessions",
        "inactivity_timeout_hours": 8,
        "archive_project_id": "",
        "archive_source_type": "session_memory",
    },
}

PROJECT_DEFAULTS: dict[str, object] = {
    "project": {"name": "", "description": "", "tags": []},
    "indexing": {
        "include_paths": ["docs", "src", "notes"],
        "exclude_patterns": [".git", "dist", "build", ".rag"],
    },
    "models": {
        "analysis_model": "mistral-small-latest",
        "answer_model": "mistral-small-latest",
        "embedding_model": "codestral-embed",
        "fast_structured_model": "groq-structured-default",
    },
    "chunking": {
        "chunk_size_chars": 1200,
        "overlap_chars": 180,
        "use_llm_chunk_policy": True,
    },
    "retrieval": {"top_k": 6, "max_context_chunks": 5, "context_budget_tokens": 1800},
    "memory": {
        "enabled": True,
        "retain_search_summaries": True,
        "retain_recent_queries": True,
        "max_active_facts": 20,
    },
    "consolidation": {
        "enabled": True,
        "post_sync": True,
        "trigger_after_queries": 25,
        "trigger_after_document_changes": 10,
    },
    "logging": {"level": "INFO", "save_prompt_hash_only": True},
}

PROMPT_DEFAULTS: dict[str, object] = {
    "document_classification": {"version": 1, "template": ""},
    "chunking_policy": {"version": 1, "template": ""},
    "chunk_summary": {"version": 1, "template": ""},
    "document_summary": {"version": 1, "template": ""},
    "project_summary_refresh": {"version": 1, "template": ""},
    "entity_extraction": {"version": 1, "template": ""},
    "query_rewrite": {"version": 1, "template": ""},
    "answer_with_grounding": {"version": 1, "template": ""},
    "memory_consolidation": {"version": 1, "template": ""},
}

REGISTRY_SCHEMA_SQL = """
create table if not exists projects (
  project_id text primary key,
  project_name text not null,
  root_path text not null,
  status text not null,
  last_seen_at text not null
);
"""


def copy_workspace_defaults() -> dict[str, object]:
    """Return a deep copy of workspace defaults."""
    return deepcopy(WORKSPACE_DEFAULTS)


def copy_project_defaults() -> dict[str, object]:
    """Return a deep copy of project defaults."""
    return deepcopy(PROJECT_DEFAULTS)


def copy_prompt_defaults() -> dict[str, object]:
    """Return a deep copy of prompt defaults."""
    return deepcopy(PROMPT_DEFAULTS)
