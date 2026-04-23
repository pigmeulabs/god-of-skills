"""Memory consolidation service."""

from __future__ import annotations

import json
from hashlib import sha256

from pigmeu_never_forget.domain.models import ConsolidationPlan, ConsolidationResult, ProjectContext
from pigmeu_never_forget.services.memory_index import MemoryIndexService
from pigmeu_never_forget.storage.sqlite import sqlite_cursor


class MemoryConsolidationService:
    """Consolidate project memory incrementally."""

    def __init__(self, memory_index: MemoryIndexService | None = None) -> None:
        self._memory_index = memory_index or MemoryIndexService()

    def build_plan(self, project: ProjectContext, signals: dict[str, object]) -> ConsolidationPlan:
        """Build a consolidation plan from recent signals."""
        operations = [
            {"operation": "prune_duplicates"},
            {"operation": "refresh_project_summary"},
            {"operation": "rebuild_active_facts"},
        ]
        return ConsolidationPlan(project_id=project.project_id, signals=signals, operations=operations)

    def execute(self, project: ProjectContext, plan: ConsolidationPlan) -> ConsolidationResult:
        """Execute a consolidation plan."""
        operations_applied = 0
        audit_records = 0

        duplicate_fact_ids = self._find_duplicate_fact_ids(project)
        if duplicate_fact_ids:
            with sqlite_cursor(project.memory_db_path) as connection:
                for fact_id in duplicate_fact_ids:
                    connection.execute(
                        "update memory_facts set status = 'discarded', updated_at = datetime('now') where fact_id = ?",
                        (fact_id,),
                    )
                    self._insert_audit(
                        connection=connection,
                        project_id=project.project_id,
                        operation="prune",
                        target_type="memory_fact",
                        target_id=fact_id,
                        reason="duplicate_text",
                    )
                    audit_records += 1
            operations_applied += 1

        self._memory_index.refresh_project_memory(project)
        operations_applied += 1

        return ConsolidationResult(
            project_id=project.project_id,
            operations_applied=operations_applied,
            audit_records=audit_records,
            warnings=[],
        )

    def _find_duplicate_fact_ids(self, project: ProjectContext) -> list[str]:
        with sqlite_cursor(project.memory_db_path) as connection:
            rows = connection.execute(
                """
                select fact_id, fact_text, created_at
                from memory_facts
                where project_id = ? and status = 'active'
                order by created_at asc
                """,
                (project.project_id,),
            ).fetchall()
        seen: set[str] = set()
        duplicates: list[str] = []
        for row in rows:
            key = str(row["fact_text"]).strip().lower()
            if key in seen:
                duplicates.append(str(row["fact_id"]))
            else:
                seen.add(key)
        return duplicates

    def _insert_audit(
        self,
        connection,
        project_id: str,
        operation: str,
        target_type: str,
        target_id: str,
        reason: str,
    ) -> None:
        audit_id = f"audit_{sha256(f'{project_id}:{operation}:{target_id}'.encode('utf-8')).hexdigest()[:18]}"
        connection.execute(
            """
            insert or replace into consolidation_audit(
              audit_id, project_id, job_id, operation, target_type, target_id,
              before_json, after_json, reason, confidence, model, created_at
            ) values (?, ?, NULL, ?, ?, ?, NULL, NULL, ?, NULL, 'local', datetime('now'))
            """,
            (audit_id, project_id, operation, target_type, target_id, reason),
        )
