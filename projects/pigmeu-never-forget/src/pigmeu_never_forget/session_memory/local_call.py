"""Local tool dispatcher for session memory MCP wrappers."""

from __future__ import annotations

import argparse
import json
from typing import Any

from pigmeu_never_forget.session_memory.adapter import SessionMemoryAdapter


def _parse_json(value: str | None) -> dict[str, Any]:
    if not value:
        return {}
    payload = json.loads(value)
    return payload if isinstance(payload, dict) else {}


def _dispatch(adapter: SessionMemoryAdapter, tool: str, payload: dict[str, Any]) -> dict[str, Any]:
    handlers = {
        "start_session": adapter.start_session,
        "append_turn": adapter.append_turn,
        "update_metrics": adapter.update_metrics,
        "finalize_session": adapter.finalize_session,
        "archive_session": adapter.archive_session,
        "record_response": adapter.record_response,
        "rollover_stale_sessions": adapter.rollover_stale_sessions,
        "get_session_status": adapter.get_session_status,
        "latest_session": lambda _: adapter.latest_session(),
    }
    if tool not in handlers:
        raise ValueError(f"Unsupported session tool: {tool}")
    handler = handlers[tool]
    if tool == "latest_session":
        return handler(payload)  # type: ignore[call-arg]
    return handler(payload)  # type: ignore[call-arg]


def main() -> int:
    parser = argparse.ArgumentParser(prog="pnf-session-memory-call")
    parser.add_argument("tool", help="Tool name.")
    parser.add_argument("--payload", help="JSON payload for the tool.")
    parser.add_argument("--repo-root", help="Optional repository root path.")
    parser.add_argument("--config", help="Optional workspace config path.")
    parser.add_argument("--archive-project-id", help="Archive target project id.")
    args = parser.parse_args()
    adapter = SessionMemoryAdapter(
        repo_root=args.repo_root,
        config_path=args.config,
        archive_project_id=args.archive_project_id,
    )
    result = _dispatch(adapter, args.tool, _parse_json(args.payload))
    print(json.dumps(result, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
