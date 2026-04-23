"""CLI for session memory management."""

from __future__ import annotations

import argparse
import json
from typing import Any

from pigmeu_never_forget.session_memory.adapter import SessionMemoryAdapter


def _parse_payload(raw: str | None) -> dict[str, Any]:
    if not raw:
        return {}
    payload = json.loads(raw)
    return payload if isinstance(payload, dict) else {}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="pnf-session")
    parser.add_argument("--config", help="Optional workspace config path.")
    parser.add_argument("--repo-root", help="Optional repository root path.")
    parser.add_argument("--archive-project-id", help="Archive target project id.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    for name in (
        "start-session",
        "append-turn",
        "record-response",
        "update-metrics",
        "finalize-session",
        "archive-session",
        "rollover-stale-sessions",
        "status",
    ):
        command = subparsers.add_parser(name, help=f"Run {name.replace('-', ' ')}.")
        command.add_argument("--payload", help="JSON payload for the command.")

    latest = subparsers.add_parser("latest", help="Return the latest session.")
    latest.add_argument("--request-id", help="Optional request id.")

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    adapter = SessionMemoryAdapter(
        repo_root=args.repo_root,
        config_path=args.config,
        archive_project_id=args.archive_project_id,
    )

    if args.command == "latest":
        result = adapter.latest_session(request_id=args.request_id)
    else:
        payload = _parse_payload(args.payload)
        if args.command == "start-session":
            result = adapter.start_session(payload)
        elif args.command == "append-turn":
            result = adapter.append_turn(payload)
        elif args.command == "record-response":
            result = adapter.record_response(payload)
        elif args.command == "update-metrics":
            result = adapter.update_metrics(payload)
        elif args.command == "finalize-session":
            result = adapter.finalize_session(payload)
        elif args.command == "archive-session":
            result = adapter.archive_session(payload)
        elif args.command == "rollover-stale-sessions":
            result = adapter.rollover_stale_sessions(payload)
        elif args.command == "status":
            result = adapter.get_session_status(payload)
        else:
            parser.error(f"Unsupported command: {args.command}")
            return 2

    print(json.dumps(result, indent=2, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
