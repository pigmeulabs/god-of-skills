#!/usr/bin/env python3
"""Finalize and archive a session file."""

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
        if not session_stem:
            _, latest, _ = run_with_mcp_fallback("latest_session", {}, ["latest"])
            session = latest.get("data", {}).get("session") or latest.get("data") or {}
            session_stem = session.get("session_stem") if isinstance(session, dict) else None
        if not session_stem:
            raise RuntimeError("No session stem available to finalize.")
        finalize_payload = {"session_stem": session_stem, "archive": True}
        command, result, backend = run_with_mcp_fallback(
            "finalize_session",
            finalize_payload,
            ["finalize-session", "--payload", json.dumps(finalize_payload, ensure_ascii=True)],
        )
        print_envelope(
            command,
            "Sessao finalizada e arquivada.",
            "A proxima sessao pode ser iniciada com ensure_session.py.",
            {"backend": backend, "result": result},
        )
        return 0
    except Exception as exc:  # noqa: BLE001
        fail(str(exc))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
