"""Memory index services for summaries, entities and compact facts."""

from __future__ import annotations

import json
import re
from hashlib import sha256

from pigmeu_never_forget.domain.models import AnalysisResult, ProjectContext, SourceDocument
from pigmeu_never_forget.storage.sqlite import sqlite_cursor


class MemoryIndexService:
    """Maintain document and project memory structures."""

    def update_document_memory(
        self,
        project: ProjectContext,
        doc_id: str,
        path: str,
        document: SourceDocument,
        analysis: AnalysisResult,
    ) -> None:
        """Persist summaries, entities and facts for one document."""
        summary_short, summary_full = self._summarize(document.raw_text)
        topics = self._extract_topics(document.raw_text)
        with sqlite_cursor(project.state_db_path) as state_connection:
            state_connection.execute(
                """
                update documents
                set summary_short = ?, summary_full = ?, topics_json = ?
                where doc_id = ?
                """,
                (summary_short, summary_full, json.dumps(topics), doc_id),
            )

        self._upsert_entities(project, analysis.entities, source_ref=path)
        self._upsert_fact(project, doc_id, summary_short, source_ref=path, confidence=0.8)
        self.refresh_project_memory(project)

    def refresh_project_memory(self, project: ProjectContext) -> None:
        """Refresh project summary and compact facts from current state."""
        with sqlite_cursor(project.state_db_path) as state_connection:
            rows = state_connection.execute(
                """
                select summary_short, summary_full
                from documents
                where project_id = ? and status = 'active'
                order by last_indexed_at desc
                """,
                (project.project_id,),
            ).fetchall()
        summaries = [str(row["summary_short"] or "") for row in rows if str(row["summary_short"] or "").strip()]
        details = [str(row["summary_full"] or "") for row in rows if str(row["summary_full"] or "").strip()]

        summary_short = " | ".join(summaries[:3])[:500] if summaries else ""
        summary_full = "\n\n".join(details[:10])[:4000] if details else summary_short
        active_facts = self._get_top_facts(project, limit=20)
        payload = json.dumps(active_facts, ensure_ascii=True)

        with sqlite_cursor(project.memory_db_path) as memory_connection:
            memory_connection.execute(
                """
                insert into project_summary(project_id, version, summary_short, summary_full, active_facts_compact_json, updated_at)
                values (?, 1, ?, ?, ?, datetime('now'))
                on conflict(project_id) do update set
                  version = project_summary.version + 1,
                  summary_short = excluded.summary_short,
                  summary_full = excluded.summary_full,
                  active_facts_compact_json = excluded.active_facts_compact_json,
                  updated_at = excluded.updated_at
                """,
                (project.project_id, summary_short, summary_full, payload),
            )

    def _summarize(self, text: str) -> tuple[str, str]:
        cleaned = " ".join(text.split())
        if not cleaned:
            return "", ""
        sentences = re.split(r"(?<=[.!?])\s+", cleaned)
        short = " ".join(sentences[:2]).strip()[:320]
        full = " ".join(sentences[:8]).strip()[:2000]
        return short, full

    def _extract_topics(self, text: str) -> list[str]:
        words = re.findall(r"\b[a-zA-Z][a-zA-Z0-9_-]{4,}\b", text.lower())
        rank: dict[str, int] = {}
        for word in words:
            if word in {"about", "there", "where", "which", "project", "token"}:
                continue
            rank[word] = rank.get(word, 0) + 1
        return [item[0] for item in sorted(rank.items(), key=lambda pair: pair[1], reverse=True)[:10]]

    def _upsert_entities(self, project: ProjectContext, entities: list[str], source_ref: str) -> None:
        with sqlite_cursor(project.memory_db_path) as connection:
            for entity in entities:
                entity_id = f"ent_{sha256(f'{project.project_id}:{entity}'.encode('utf-8')).hexdigest()[:16]}"
                connection.execute(
                    """
                    insert into entities(entity_id, project_id, name, type, description, canonical, created_at, updated_at)
                    values (?, ?, ?, 'keyword', '', 1, datetime('now'), datetime('now'))
                    on conflict(entity_id) do update set updated_at = datetime('now')
                    """,
                    (entity_id, project.project_id, entity),
                )
                alias_id = f"alias_{sha256(f'{entity_id}:{entity.lower()}'.encode('utf-8')).hexdigest()[:16]}"
                connection.execute(
                    """
                    insert or ignore into entity_aliases(alias_id, entity_id, alias, confidence, source_ref)
                    values (?, ?, ?, 0.9, ?)
                    """,
                    (alias_id, entity_id, entity.lower(), source_ref),
                )

    def _upsert_fact(
        self,
        project: ProjectContext,
        doc_id: str,
        fact_text: str,
        source_ref: str,
        confidence: float,
    ) -> None:
        if not fact_text.strip():
            return
        fact_id = f"fact_{sha256(f'{project.project_id}:{doc_id}:{fact_text}'.encode('utf-8')).hexdigest()[:20]}"
        with sqlite_cursor(project.memory_db_path) as connection:
            connection.execute(
                """
                insert into memory_facts(
                  fact_id, project_id, fact_text, scope, confidence, status, source_ref,
                  evidence_json, created_at, updated_at, superseded_by
                ) values (?, ?, ?, 'document', ?, 'active', ?, '[]', datetime('now'), datetime('now'), NULL)
                on conflict(fact_id) do update set
                  confidence = excluded.confidence,
                  status = 'active',
                  updated_at = datetime('now'),
                  source_ref = excluded.source_ref
                """,
                (fact_id, project.project_id, fact_text, confidence, source_ref),
            )

    def _get_top_facts(self, project: ProjectContext, limit: int) -> list[str]:
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
