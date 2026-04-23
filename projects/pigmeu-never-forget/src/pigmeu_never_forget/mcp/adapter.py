"""Reusable MCP adapter logic for tools/resources and local calls."""

from __future__ import annotations

import json
import uuid
from typing import Any

from pigmeu_never_forget.app import create_application
from pigmeu_never_forget.mcp.contracts import error_from_exception, success
from pigmeu_never_forget.storage.sqlite import sqlite_cursor


def _rid(request_id: str | None) -> str:
    return request_id or f"req_{uuid.uuid4().hex[:12]}"


class PNFMCPAdapter:
    """Thin MCP adapter over WorkspaceService with standardized envelopes."""

    def __init__(self, config_path: str | None = None) -> None:
        self.workspace_service = create_application(config_path)
        self.workspace_service.initialize_workspace()

    def list_projects(self, request_id: str | None = None) -> dict[str, Any]:
        rid = _rid(request_id)
        try:
            discovered = self.workspace_service.discover_projects()
            return success({"projects": discovered.get("projects", [])}, request_id=rid)
        except Exception as exc:  # noqa: BLE001
            return error_from_exception(exc, request_id=rid)

    def sync_project(
        self,
        project_id: str,
        mode: str = "incremental",
        force: bool = False,
        request_id: str | None = None,
    ) -> dict[str, Any]:
        rid = _rid(request_id)
        del mode, force
        try:
            payload = self.workspace_service.sync_project(project_id)
            self._log_event(project_id, rid, "sync_project", "ok", payload)
            return success(payload, project_id=project_id, request_id=rid)
        except Exception as exc:  # noqa: BLE001
            self._log_event(project_id, rid, "sync_project", "error", {"error": str(exc)})
            return error_from_exception(exc, request_id=rid)

    def index_text(
        self,
        project_id: str,
        title: str,
        text: str,
        source_type: str = "inline_text",
        tags: list[str] | None = None,
        request_id: str | None = None,
    ) -> dict[str, Any]:
        rid = _rid(request_id)
        try:
            payload = self.workspace_service.index_text(
                project_id=project_id,
                title=title,
                text=text,
                source_type=source_type,
                tags=tags or [],
            )
            self._log_event(project_id, rid, "index_text", "ok", payload)
            return success(payload, project_id=project_id, request_id=rid)
        except Exception as exc:  # noqa: BLE001
            self._log_event(project_id, rid, "index_text", "error", {"error": str(exc)})
            return error_from_exception(exc, request_id=rid)

    def search_project(
        self,
        project_id: str,
        query: str,
        top_k: int = 8,
        expand: bool = False,
        request_id: str | None = None,
    ) -> dict[str, Any]:
        rid = _rid(request_id)
        del expand
        try:
            payload = self.workspace_service.search_project(project_id, query, top_k=top_k)
            self._log_event(project_id, rid, "search_project", "ok", {"hits": len(payload.get("hits", []))})
            return success(payload, project_id=project_id, request_id=rid)
        except Exception as exc:  # noqa: BLE001
            self._log_event(project_id, rid, "search_project", "error", {"error": str(exc)})
            return error_from_exception(exc, request_id=rid)

    def ask_project(
        self,
        project_id: str,
        question: str,
        top_k: int = 6,
        allow_summary_only: bool = True,
        request_id: str | None = None,
    ) -> dict[str, Any]:
        rid = _rid(request_id)
        del allow_summary_only
        try:
            payload = self.workspace_service.ask_project(project_id, question, top_k=top_k)
            self._log_event(project_id, rid, "ask_project", "ok", {"sources": len(payload.get("sources", []))})
            return success(payload, project_id=project_id, request_id=rid)
        except Exception as exc:  # noqa: BLE001
            self._log_event(project_id, rid, "ask_project", "error", {"error": str(exc)})
            return error_from_exception(exc, request_id=rid)

    def get_project_stats(self, project_id: str, request_id: str | None = None) -> dict[str, Any]:
        rid = _rid(request_id)
        try:
            payload = self.workspace_service.get_project_stats(project_id)
            return success({"stats": payload}, project_id=project_id, request_id=rid)
        except Exception as exc:  # noqa: BLE001
            return error_from_exception(exc, request_id=rid)

    def consolidate_project(
        self,
        project_id: str,
        mode: str = "incremental",
        request_id: str | None = None,
    ) -> dict[str, Any]:
        rid = _rid(request_id)
        del mode
        try:
            payload = self.workspace_service.consolidate_project(project_id)
            self._log_event(project_id, rid, "consolidate_project", "ok", payload)
            return success(payload, project_id=project_id, request_id=rid)
        except Exception as exc:  # noqa: BLE001
            self._log_event(project_id, rid, "consolidate_project", "error", {"error": str(exc)})
            return error_from_exception(exc, request_id=rid)

    def get_job_status(
        self,
        project_id: str,
        job_id: str,
        request_id: str | None = None,
    ) -> dict[str, Any]:
        rid = _rid(request_id)
        try:
            payload = self.workspace_service.get_job_status(project_id, job_id)
            return success({"job": payload}, project_id=project_id, request_id=rid)
        except Exception as exc:  # noqa: BLE001
            return error_from_exception(exc, request_id=rid)

    def resource_projects(self) -> str:
        return json.dumps(self.list_projects(request_id=_rid(None)), ensure_ascii=True)

    def resource_project_summary(self, project_id: str) -> str:
        rid = _rid(None)
        try:
            context = self.workspace_service._resolve_project_context(project_id)  # noqa: SLF001
            with sqlite_cursor(context.memory_db_path) as connection:
                row = connection.execute(
                    """
                    select summary_short, summary_full, active_facts_compact_json
                    from project_summary
                    where project_id = ?
                    """,
                    (project_id,),
                ).fetchone()
            if row is None:
                payload = {
                    "project_id": project_id,
                    "summary_short": "",
                    "summary_full": "",
                    "active_facts_compact": [],
                }
            else:
                compact_raw = row["active_facts_compact_json"]
                payload = {
                    "project_id": project_id,
                    "summary_short": str(row["summary_short"] or ""),
                    "summary_full": str(row["summary_full"] or ""),
                    "active_facts_compact": json.loads(compact_raw) if compact_raw else [],
                }
            return json.dumps(success(payload, project_id=project_id, request_id=rid), ensure_ascii=True)
        except Exception as exc:  # noqa: BLE001
            return json.dumps(error_from_exception(exc, request_id=rid), ensure_ascii=True)

    def resource_project_stats(self, project_id: str) -> str:
        rid = _rid(None)
        try:
            payload = self.workspace_service.get_project_stats(project_id)
            return json.dumps(success({"stats": payload}, project_id=project_id, request_id=rid), ensure_ascii=True)
        except Exception as exc:  # noqa: BLE001
            return json.dumps(error_from_exception(exc, request_id=rid), ensure_ascii=True)

    def resource_project_job(self, project_id: str, job_id: str) -> str:
        rid = _rid(None)
        try:
            payload = self.workspace_service.get_job_status(project_id, job_id)
            return json.dumps(success({"job": payload}, project_id=project_id, request_id=rid), ensure_ascii=True)
        except Exception as exc:  # noqa: BLE001
            return json.dumps(error_from_exception(exc, request_id=rid), ensure_ascii=True)

    def _log_event(
        self,
        project_id: str,
        request_id: str,
        event_type: str,
        status: str,
        payload: dict[str, Any],
    ) -> None:
        try:
            context = self.workspace_service._resolve_project_context(project_id)  # noqa: SLF001
            event_id = f"evt_{uuid.uuid4().hex}"
            with sqlite_cursor(context.state_db_path) as connection:
                connection.execute(
                    """
                    insert into log_events(
                      event_id, project_id, job_id, timestamp, level, service, event_type, trace_id, payload_json
                    ) values (?, ?, NULL, datetime('now'), ?, 'mcp', ?, ?, ?)
                    """,
                    (
                        event_id,
                        project_id,
                        "INFO" if status == "ok" else "ERROR",
                        event_type,
                        request_id,
                        json.dumps({"status": status, **payload}, ensure_ascii=True),
                    ),
                )
        except Exception:
            return

