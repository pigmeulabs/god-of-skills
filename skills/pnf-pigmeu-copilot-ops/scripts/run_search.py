#!/usr/bin/env python3
"""Run search against pigmeu-copilot knowledge base."""

from __future__ import annotations

import argparse

from common import fail, print_envelope, project_id, run_with_mcp_fallback


def main() -> int:
    parser = argparse.ArgumentParser(description="Search pigmeu-copilot knowledge base.")
    parser.add_argument("query", help="Semantic query.")
    parser.add_argument("--top-k", type=int, default=8, help="Number of hits.")
    args = parser.parse_args()

    try:
        cmd, data, mode = run_with_mcp_fallback(
            mcp_tool="search_project",
            mcp_payload={"project_id": project_id(), "query": args.query, "top_k": args.top_k, "expand": False},
            cli_args=["search", project_id(), args.query, "--top-k", str(args.top_k)],
        )
    except Exception as exc:  # noqa: BLE001
        fail(str(exc))
        return 1

    data_root = data.get("data", data)
    hits = data_root.get("hits", [])
    summary = f"Busca concluida via {mode} com {len(hits)} hits."
    next_step = "Use run_ask.py para resposta grounded com fontes."
    print_envelope(command=cmd, summary=summary, next_step=next_step, data=data_root)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
