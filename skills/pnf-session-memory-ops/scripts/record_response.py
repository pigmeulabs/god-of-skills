#!/usr/bin/env python3
"""Record one assistant response with automatic session lifecycle handling."""

from __future__ import annotations

import argparse
import json

from common import fail, print_envelope, read_payload, run_with_mcp_fallback


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--payload", help="JSON payload for the response turn.")
    args = parser.parse_args()

    try:
        payload = read_payload(args.payload)
        command, result, backend = run_with_mcp_fallback(
            "record_response",
            payload,
            ["record-response", "--payload", json.dumps(payload, ensure_ascii=True)],
        )
        print_envelope(
            command,
            "Resposta registrada com sessao ativa e arquivo incremental atualizado.",
            "Repita record_response.py apos cada resposta do agente e finalize no encerramento.",
            {"backend": backend, "result": result},
        )
        return 0
    except Exception as exc:  # noqa: BLE001
        fail(str(exc))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
