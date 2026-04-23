#!/usr/bin/env python3
"""Ensure there is an active session file."""

from __future__ import annotations

import json
import os

from common import archive_project_id, fail, print_envelope, repo_path, run_with_mcp_fallback


def _default_payload() -> dict[str, object]:
    repo = repo_path()
    return {
        "project_name": os.environ.get("PNF_SESSION_PROJECT_NAME", repo.name),
        "project_id": os.environ.get("PNF_SESSION_PROJECT_ID", repo.name),
        "summary_short": os.environ.get("PNF_SESSION_SUMMARY_SHORT", ""),
        "summary_full": os.environ.get("PNF_SESSION_SUMMARY_FULL", ""),
        "humans": [value for value in [os.environ.get("PNF_SESSION_HUMAN")] if value],
        "agents": [value for value in [os.environ.get("PNF_SESSION_AGENT", "codex")] if value],
        "model": os.environ.get("PNF_SESSION_MODEL"),
        "archive_project_id": archive_project_id(),
    }


def main() -> int:
    try:
        latest_command, latest_result, backend = run_with_mcp_fallback(
            "latest_session",
            {},
            ["latest"],
        )
        latest = latest_result.get("data", {}).get("session") or latest_result.get("data")
        if isinstance(latest, dict) and latest and not latest.get("is_stale") and latest.get("status") == "active":
            print_envelope(
                latest_command,
                "Sessao ativa localizada.",
                "Use append_turn.py para registrar a proxima resposta.",
                {"session": latest, "backend": backend},
            )
            return 0
        if isinstance(latest, dict) and latest.get("session_stem") and latest.get("status") == "active":
            finalize_payload = {"session_stem": latest["session_stem"], "archive": True}
            finalize_command, finalize_result, _ = run_with_mcp_fallback(
                "finalize_session",
                finalize_payload,
                ["finalize-session", "--payload", json.dumps(finalize_payload, ensure_ascii=True)],
            )
        else:
            finalize_command = None
            finalize_result = {}

        start_payload = _default_payload()
        start_command, start_result, start_backend = run_with_mcp_fallback(
            "start_session",
            start_payload,
            ["start-session", "--payload", json.dumps(start_payload, ensure_ascii=True)],
        )
        print_envelope(
            start_command,
            "Nova sessao ativa criada.",
            "Use append_turn.py apos cada resposta do agente.",
            {
                "latest_command": latest_command,
                "latest_session": latest,
                "finalize_command": finalize_command,
                "finalize_result": finalize_result,
                "start_result": start_result,
                "backend": start_backend,
            },
        )
        return 0
    except Exception as exc:  # noqa: BLE001
        fail(str(exc))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
