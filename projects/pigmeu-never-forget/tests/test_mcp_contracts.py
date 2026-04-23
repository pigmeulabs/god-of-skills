from __future__ import annotations

from pigmeu_never_forget.domain.enums import ErrorCode
from pigmeu_never_forget.domain.errors import AppError
from pigmeu_never_forget.mcp.contracts import error_from_exception, success


def test_mcp_success_envelope_includes_meta() -> None:
    payload = success({"value": 1}, project_id="pigmeu-copilot", request_id="req-1")
    assert payload["status"] == "ok"
    assert payload["data"]["value"] == 1
    assert payload["meta"]["project_id"] == "pigmeu-copilot"
    assert payload["meta"]["request_id"] == "req-1"


def test_mcp_success_without_meta_is_valid() -> None:
    payload = success({"value": 2})
    assert payload["status"] == "ok"
    assert payload["data"]["value"] == 2
    assert "meta" not in payload


def test_mcp_error_envelope_maps_app_error() -> None:
    err = AppError(
        code=ErrorCode.PROJECT_LOCKED,
        message="Project lock in use",
        retryable=True,
        details={"project_id": "pigmeu-copilot"},
    )
    payload = error_from_exception(err, request_id="req-2")
    assert payload["status"] == "error"
    assert payload["error"]["code"] == "PROJECT_LOCKED"
    assert payload["error"]["retryable"] is True
    assert payload["meta"]["request_id"] == "req-2"


def test_mcp_error_envelope_maps_not_found() -> None:
    payload = error_from_exception(FileNotFoundError("Project not found: nope"))
    assert payload["status"] == "error"
    assert payload["error"]["code"] == "PROJECT_NOT_FOUND"
