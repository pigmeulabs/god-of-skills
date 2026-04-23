"""Retrieval service with summary-first context assembly."""

from __future__ import annotations

import json
from dataclasses import dataclass

from pigmeu_never_forget.domain.models import ProjectContext, RetrievalHit
from pigmeu_never_forget.services.embedding import EmbeddingService
from pigmeu_never_forget.services.vector_store import VectorStoreService
from pigmeu_never_forget.storage.sqlite import sqlite_cursor


@dataclass(slots=True)
class RetrievalContext:
    """Context fragments used for answer generation."""

    query: str
    rewritten_query: str
    summary_short: str
    facts: list[str]
    hits: list[RetrievalHit]
    budget_tokens: int


class RetrievalService:
    """Build and execute retrieval plans."""

    def __init__(
        self,
        embedding: EmbeddingService | None = None,
        vector_store: VectorStoreService | None = None,
    ) -> None:
        self._embedding = embedding or EmbeddingService()
        self._vector_store = vector_store or VectorStoreService()

    def search(self, project: ProjectContext, query: str, top_k: int = 8) -> list[RetrievalHit]:
        """Return vector hits for a project."""
        query_vector = self._embedding.embed_query(project, query)
        return self._vector_store.search(project, query_vector, top_k=top_k)

    def build_context(self, project: ProjectContext, query: str, top_k: int = 6) -> RetrievalContext:
        """Build summary-first retrieval context."""
        rewritten = self._rewrite_query(project, query)
        summary = self._get_project_summary_short(project)
        facts = self._get_active_facts(project, limit=20)
        hits = self.search(project, rewritten, top_k=top_k)
        budget = int(project.settings["project_settings"]["retrieval"]["context_budget_tokens"])
        return RetrievalContext(
            query=query,
            rewritten_query=rewritten,
            summary_short=summary,
            facts=facts,
            hits=hits,
            budget_tokens=budget,
        )

    def save_query_result(
        self,
        project: ProjectContext,
        query: str,
        rewritten_query: str,
        response_summary: str,
        sources: list[dict[str, object]],
        latency_ms: int,
    ) -> None:
        """Persist query history in memory.db."""
        query_id = f"query_{abs(hash((project.project_id, query, rewritten_query, latency_ms)))}"
        with sqlite_cursor(project.memory_db_path) as connection:
            connection.execute(
                """
                insert or replace into query_history(
                  query_id, project_id, query_text, rewritten_query, response_summary, sources_json, latency_ms, created_at
                ) values (?, ?, ?, ?, ?, ?, ?, datetime('now'))
                """,
                (
                    query_id,
                    project.project_id,
                    query,
                    rewritten_query,
                    response_summary,
                    json.dumps(sources),
                    latency_ms,
                ),
            )

    def save_api_call(
        self,
        project: ProjectContext,
        provider: str,
        model: str,
        operation: str,
        duration_ms: int,
        success: bool,
    ) -> None:
        """Persist a synthetic api call trace in state.db."""
        call_id = f"call_{abs(hash((project.project_id, operation, duration_ms)))}"
        with sqlite_cursor(project.state_db_path) as connection:
            connection.execute(
                """
                insert or replace into api_calls(
                  call_id, project_id, job_id, provider, model, api_key_name, operation,
                  duration_ms, success, http_status, retry_count, input_tokens_est, output_tokens_est,
                  prompt_template_name, prompt_template_version, input_hash, response_hash, created_at
                ) values (?, ?, NULL, ?, ?, NULL, ?, ?, ?, NULL, 0, NULL, NULL, NULL, NULL, NULL, NULL, datetime('now'))
                """,
                (
                    call_id,
                    project.project_id,
                    provider,
                    model,
                    operation,
                    duration_ms,
                    1 if success else 0,
                ),
            )

    def get_project_stats(self, project: ProjectContext) -> dict[str, object]:
        """Return basic project stats."""
        with sqlite_cursor(project.state_db_path) as state_connection:
            documents = state_connection.execute(
                "select count(*) as total from documents where status = 'active'"
            ).fetchone()["total"]
            chunks = state_connection.execute(
                "select count(*) as total from chunks where active = 1"
            ).fetchone()["total"]
            api_calls = state_connection.execute(
                "select count(*) as total from api_calls"
            ).fetchone()["total"]
        with sqlite_cursor(project.memory_db_path) as memory_connection:
            facts = memory_connection.execute(
                "select count(*) as total from memory_facts where status = 'active'"
            ).fetchone()["total"]
            entities = memory_connection.execute(
                "select count(*) as total from entities"
            ).fetchone()["total"]
            queries = memory_connection.execute(
                "select count(*) as total from query_history"
            ).fetchone()["total"]
        return {
            "project_id": project.project_id,
            "documents_active": documents,
            "chunks_active": chunks,
            "facts_active": facts,
            "entities_total": entities,
            "queries_total": queries,
            "api_calls_total": api_calls,
        }

    def _rewrite_query(self, project: ProjectContext, query: str) -> str:
        # Stage-5 base rewrite: include top aliases if present.
        aliases: list[str] = []
        with sqlite_cursor(project.memory_db_path) as connection:
            rows = connection.execute(
                """
                select alias
                from entity_aliases
                order by confidence desc, alias asc
                limit 5
                """
            ).fetchall()
            aliases = [str(row["alias"]) for row in rows]
        if not aliases:
            return query
        return f"{query}\nAliases: {', '.join(aliases)}"

    def _get_project_summary_short(self, project: ProjectContext) -> str:
        with sqlite_cursor(project.memory_db_path) as connection:
            row = connection.execute(
                "select summary_short from project_summary where project_id = ?",
                (project.project_id,),
            ).fetchone()
        if row is None:
            return ""
        return str(row["summary_short"] or "")

    def _get_active_facts(self, project: ProjectContext, limit: int) -> list[str]:
        with sqlite_cursor(project.memory_db_path) as connection:
            rows = connection.execute(
                """
                select fact_text
                from memory_facts
                where project_id = ? and status = 'active'
                order by confidence desc, updated_at desc
                limit ?
                """,
                (project.project_id, limit),
            ).fetchall()
        return [str(row["fact_text"]) for row in rows]
