"""FastAPI thin adapter over the core workspace services."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Any

from pigmeu_never_forget.app import create_application
from pigmeu_never_forget.mcp.contracts import error_from_exception, success


@dataclass(slots=True)
class RequestContext:
    """Request-scoped metadata."""

    request_id: str


def _request_id(value: str | None) -> str:
    return (value or "").strip() or f"req_{uuid.uuid4().hex[:12]}"


def create_http_app(config_path: str | None = None):
    """Create FastAPI application with project-aware routes."""
    try:
        from fastapi import FastAPI, Header
    except Exception as exc:  # noqa: BLE001
        raise RuntimeError("FastAPI is not installed. Install with `pip install \".[api]\"`.") from exc

    app = FastAPI(title="pigmeu-never-forget", version="0.1.0")
    workspace_service = create_application(config_path)
    workspace_service.initialize_workspace()

    def ctx(x_request_id: str | None) -> RequestContext:
        return RequestContext(request_id=_request_id(x_request_id))

    @app.get("/health")
    def health(x_request_id: str | None = Header(default=None, alias="X-Request-Id")) -> dict[str, Any]:
        context = ctx(x_request_id)
        return success({"service": "pigmeu-never-forget", "status": "ok"}, request_id=context.request_id)

    @app.get("/projects")
    def list_projects(x_request_id: str | None = Header(default=None, alias="X-Request-Id")) -> dict[str, Any]:
        context = ctx(x_request_id)
        try:
            result = workspace_service.discover_projects()
            return success(result, request_id=context.request_id)
        except Exception as exc:  # noqa: BLE001
            return error_from_exception(exc, request_id=context.request_id)

    @app.post("/projects/discover")
    def discover_projects(x_request_id: str | None = Header(default=None, alias="X-Request-Id")) -> dict[str, Any]:
        context = ctx(x_request_id)
        try:
            result = workspace_service.discover_projects()
            return success(result, request_id=context.request_id)
        except Exception as exc:  # noqa: BLE001
            return error_from_exception(exc, request_id=context.request_id)

    @app.post("/projects/{project_id}/sync")
    def sync_project(
        project_id: str,
        payload: dict[str, Any] | None = None,
        x_request_id: str | None = Header(default=None, alias="X-Request-Id"),
    ) -> dict[str, Any]:
        context = ctx(x_request_id)
        del payload
        try:
            result = workspace_service.sync_project(project_id)
            return success(result, project_id=project_id, request_id=context.request_id)
        except Exception as exc:  # noqa: BLE001
            return error_from_exception(exc, request_id=context.request_id)

    @app.post("/projects/{project_id}/index-text")
    def index_text(
        project_id: str,
        payload: dict[str, Any],
        x_request_id: str | None = Header(default=None, alias="X-Request-Id"),
    ) -> dict[str, Any]:
        context = ctx(x_request_id)
        try:
            result = workspace_service.index_text(
                project_id=project_id,
                title=str(payload.get("title", "")),
                text=str(payload.get("text", "")),
                source_type=str(payload.get("source_type", "inline_text")),
                tags=list(payload.get("tags", [])),
            )
            return success(result, project_id=project_id, request_id=context.request_id)
        except Exception as exc:  # noqa: BLE001
            return error_from_exception(exc, request_id=context.request_id)

    @app.post("/projects/{project_id}/search")
    def search_project(
        project_id: str,
        payload: dict[str, Any],
        x_request_id: str | None = Header(default=None, alias="X-Request-Id"),
    ) -> dict[str, Any]:
        context = ctx(x_request_id)
        try:
            result = workspace_service.search_project(
                project_id,
                query=str(payload.get("query", "")),
                top_k=int(payload.get("top_k", 8)),
            )
            return success(result, project_id=project_id, request_id=context.request_id)
        except Exception as exc:  # noqa: BLE001
            return error_from_exception(exc, request_id=context.request_id)

    @app.post("/projects/{project_id}/ask")
    def ask_project(
        project_id: str,
        payload: dict[str, Any],
        x_request_id: str | None = Header(default=None, alias="X-Request-Id"),
    ) -> dict[str, Any]:
        context = ctx(x_request_id)
        try:
            result = workspace_service.ask_project(
                project_id,
                question=str(payload.get("question", "")),
                top_k=int(payload.get("top_k", 6)),
            )
            return success(result, project_id=project_id, request_id=context.request_id)
        except Exception as exc:  # noqa: BLE001
            return error_from_exception(exc, request_id=context.request_id)

    @app.post("/projects/{project_id}/consolidate")
    def consolidate_project(
        project_id: str,
        payload: dict[str, Any] | None = None,
        x_request_id: str | None = Header(default=None, alias="X-Request-Id"),
    ) -> dict[str, Any]:
        context = ctx(x_request_id)
        del payload
        try:
            result = workspace_service.consolidate_project(project_id)
            return success(result, project_id=project_id, request_id=context.request_id)
        except Exception as exc:  # noqa: BLE001
            return error_from_exception(exc, request_id=context.request_id)

    @app.get("/projects/{project_id}/stats")
    def get_project_stats(
        project_id: str,
        x_request_id: str | None = Header(default=None, alias="X-Request-Id"),
    ) -> dict[str, Any]:
        context = ctx(x_request_id)
        try:
            result = workspace_service.get_project_stats(project_id)
            return success({"stats": result}, project_id=project_id, request_id=context.request_id)
        except Exception as exc:  # noqa: BLE001
            return error_from_exception(exc, request_id=context.request_id)

    @app.get("/projects/{project_id}/jobs/{job_id}")
    def get_job_status(
        project_id: str,
        job_id: str,
        x_request_id: str | None = Header(default=None, alias="X-Request-Id"),
    ) -> dict[str, Any]:
        context = ctx(x_request_id)
        try:
            result = workspace_service.get_job_status(project_id, job_id)
            return success({"job": result}, project_id=project_id, request_id=context.request_id)
        except Exception as exc:  # noqa: BLE001
            return error_from_exception(exc, request_id=context.request_id)

    return app

