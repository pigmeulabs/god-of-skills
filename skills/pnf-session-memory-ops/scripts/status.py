#!/usr/bin/env python3
"""Show the current session status."""

from __future__ import annotations

import argparse
import json

from common import fail, print_envelope, read_payload, run_with_mcp_fallback


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--session-stem", help="Session stem.")
    parser.add_argument("--payload", help="JSON payload.")
    args = parser.parse_args()
    try:
        payload = read_payload(args.payload)
        session_stem = args.session_stem or payload.get("session_stem")
        if session_stem:
            command, result, backend = run_with_mcp_fallback(
                "get_session_status",
                {"session_stem": session_stem},
                ["status", "--payload", json.dumps({"session_stem": session_stem}, ensure_ascii=True)],
            )
        else:
            command, result, backend = run_with_mcp_fallback("latest_session", {}, ["latest"])
        print_envelope(
            command,
            "Status da sessao recuperado.",
            "Use append_turn.py para registrar a proxima resposta ou finalize_session.py para encerrar.",
            {"backend": backend, "result": result},
        )
        return 0
    except Exception as exc:  # noqa: BLE001
        fail(str(exc))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
