#!/usr/bin/env python3
"""Run stats for pigmeu-copilot knowledge base."""

from __future__ import annotations

from common import fail, print_envelope, project_id, run_with_mcp_fallback


def main() -> int:
    try:
        cmd, data, mode = run_with_mcp_fallback(
            mcp_tool="get_project_stats",
            mcp_payload={"project_id": project_id()},
            cli_args=["stats", project_id()],
        )
    except Exception as exc:  # noqa: BLE001
        fail(str(exc))
        return 1

    data_root = data.get("data", data)
    stats = data_root.get("stats", data_root)
    docs = int(stats.get("documents_active", 0))
    chunks = int(stats.get("chunks_active", 0))
    summary = f"Stats coletados via {mode}: documents_active={docs}, chunks_active={chunks}."
    next_step = "Se os numeros estiverem baixos, execute run_sync.py."
    print_envelope(command=cmd, summary=summary, next_step=next_step, data=stats)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
