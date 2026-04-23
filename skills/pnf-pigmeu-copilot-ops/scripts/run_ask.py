#!/usr/bin/env python3
"""Run ask against pigmeu-copilot knowledge base."""

from __future__ import annotations

import argparse

from common import fail, print_envelope, project_id, run_with_mcp_fallback


def main() -> int:
    parser = argparse.ArgumentParser(description="Ask pigmeu-copilot knowledge base.")
    parser.add_argument("question", help="Question text.")
    parser.add_argument("--top-k", type=int, default=6, help="Number of retrieval hits.")
    args = parser.parse_args()

    try:
        cmd, data, mode = run_with_mcp_fallback(
            mcp_tool="ask_project",
            mcp_payload={
                "project_id": project_id(),
                "question": args.question,
                "top_k": args.top_k,
                "allow_summary_only": True,
            },
            cli_args=["ask", project_id(), args.question, "--top-k", str(args.top_k)],
        )
    except Exception as exc:  # noqa: BLE001
        fail(str(exc))
        return 1

    data_root = data.get("data", data)
    sources = data_root.get("sources", [])
    summary = f"Pergunta respondida via {mode} com {len(sources)} fontes."
    next_step = "Use run_stats.py para revisar saude e volume da base."
    print_envelope(command=cmd, summary=summary, next_step=next_step, data=data_root)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
