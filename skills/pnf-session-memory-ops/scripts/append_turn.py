#!/usr/bin/env python3
"""Append a turn to the active session file."""

from __future__ import annotations

import argparse
import json

from common import fail, print_envelope, read_payload, run_with_mcp_fallback


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--payload", help="JSON payload for the turn.")
    args = parser.parse_args()

    try:
        payload = read_payload(args.payload)
        session_stem = payload.get("session_stem")
        if not session_stem:
            _, ensure_result, _ = run_with_mcp_fallback("latest_session", {}, ["latest"])
            latest = ensure_result.get("data", {}).get("session") or ensure_result.get("data") or {}
            if isinstance(latest, dict) and latest.get("session_stem") and latest.get("status") == "active":
                payload["session_stem"] = latest["session_stem"]
                if latest.get("is_stale"):
                    _, ensure_result, _ = run_with_mcp_fallback(
                        "finalize_session",
                        {"session_stem": latest["session_stem"], "archive": True},
                        ["finalize-session", "--payload", json.dumps({"session_stem": latest["session_stem"], "archive": True})],
                    )
                    _, start_result, _ = run_with_mcp_fallback(
                        "start_session",
                        {
                            "project_name": latest.get("project_name"),
                            "project_id": latest.get("project_id"),
                        },
                        ["start-session", "--payload", json.dumps({"project_name": latest.get("project_name"), "project_id": latest.get("project_id")})],
                    )
                    payload["session_stem"] = start_result.get("data", {}).get("session_stem") or start_result.get("data", {}).get("session_id")
            else:
                _, start_result, _ = run_with_mcp_fallback(
                    "start_session",
                    {},
                    ["start-session", "--payload", "{}"],
                )
                payload["session_stem"] = start_result.get("data", {}).get("session_stem")

        command, result, backend = run_with_mcp_fallback(
            "append_turn",
            payload,
            ["append-turn", "--payload", json.dumps(payload, ensure_ascii=True)],
        )
        print_envelope(
            command,
            "Turno registrado na sessao.",
            "Continue chamando append_turn.py apos cada resposta do agente.",
            {"session_stem": payload.get("session_stem"), "backend": backend, "result": result},
        )
        return 0
    except Exception as exc:  # noqa: BLE001
        fail(str(exc))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
