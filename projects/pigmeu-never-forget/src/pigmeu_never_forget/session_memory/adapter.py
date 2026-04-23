"""MCP adapter for session memory management."""

from __future__ import annotations

import json
import uuid
from pathlib import Path
from typing import Any

from pigmeu_never_forget.mcp.contracts import error_from_exception, success
from pigmeu_never_forget.session_memory.service import SessionMemoryService


def _rid(request_id: str | None) -> str:
    return request_id or f"req_{uuid.uuid4().hex[:12]}"


class SessionMemoryAdapter:
    """Thin adapter over SessionMemoryService."""

    def __init__(
        self,
        repo_root: str | None = None,
        config_path: str | None = None,
        archive_project_id: str | None = None,
    ) -> None:
        self.service = SessionMemoryService(
            repo_root=None if repo_root is None else Path(repo_root),
            config_path=config_path,
            archive_project_id=archive_project_id,
        )

    def start_session(self, payload: dict[str, Any], request_id: str | None = None) -> dict[str, Any]:
        rid = _rid(request_id)
        try:
            result = self.service.start_session(payload)
            return success(result, request_id=rid)
        except Exception as exc:  # noqa: BLE001
            return error_from_exception(exc, request_id=rid)

    def append_turn(self, payload: dict[str, Any], request_id: str | None = None) -> dict[str, Any]:
        rid = _rid(request_id)
        try:
            result = self.service.append_turn(payload)
            return success(result, request_id=rid)
        except Exception as exc:  # noqa: BLE001
            return error_from_exception(exc, request_id=rid)

    def update_metrics(self, payload: dict[str, Any], request_id: str | None = None) -> dict[str, Any]:
        rid = _rid(request_id)
        try:
            result = self.service.update_metrics(payload)
            return success(result, request_id=rid)
        except Exception as exc:  # noqa: BLE001
            return error_from_exception(exc, request_id=rid)

    def finalize_session(self, payload: dict[str, Any], request_id: str | None = None) -> dict[str, Any]:
        rid = _rid(request_id)
        try:
            result = self.service.finalize_session(payload)
            return success(result, request_id=rid)
        except Exception as exc:  # noqa: BLE001
            return error_from_exception(exc, request_id=rid)

    def archive_session(self, payload: dict[str, Any], request_id: str | None = None) -> dict[str, Any]:
        rid = _rid(request_id)
        try:
            result = self.service.archive_session(payload)
            return success(result, request_id=rid)
        except Exception as exc:  # noqa: BLE001
            return error_from_exception(exc, request_id=rid)

    def record_response(self, payload: dict[str, Any], request_id: str | None = None) -> dict[str, Any]:
        rid = _rid(request_id)
        try:
            result = self.service.record_response(payload)
            return success(result, request_id=rid)
        except Exception as exc:  # noqa: BLE001
            return error_from_exception(exc, request_id=rid)

    def rollover_stale_sessions(self, payload: dict[str, Any], request_id: str | None = None) -> dict[str, Any]:
        rid = _rid(request_id)
        try:
            result = self.service.rollover_stale_sessions(payload)
            return success(result, request_id=rid)
        except Exception as exc:  # noqa: BLE001
            return error_from_exception(exc, request_id=rid)

    def get_session_status(self, payload: dict[str, Any], request_id: str | None = None) -> dict[str, Any]:
        rid = _rid(request_id)
        try:
            result = self.service.get_session_status(payload)
            return success(result, request_id=rid)
        except Exception as exc:  # noqa: BLE001
            return error_from_exception(exc, request_id=rid)

    def latest_session(self, request_id: str | None = None) -> dict[str, Any]:
        rid = _rid(request_id)
        try:
            result = self.service.find_latest_session()
            return success({"session": result}, request_id=rid)
        except Exception as exc:  # noqa: BLE001
            return error_from_exception(exc, request_id=rid)

    def to_json(self, payload: dict[str, Any]) -> str:
        return json.dumps(payload, ensure_ascii=True)
