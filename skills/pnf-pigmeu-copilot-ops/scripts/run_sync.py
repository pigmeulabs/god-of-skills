#!/usr/bin/env python3
"""Run bootstrap+sync for pigmeu-copilot."""

from __future__ import annotations

from common import (
    fail,
    print_envelope,
    project_id,
    project_path,
    run_pnf_cli,
    run_with_mcp_fallback,
)


def main() -> int:
    try:
        cmd_init, _ = run_pnf_cli(["init-workspace"])
        cmd_bootstrap, _ = run_pnf_cli(["bootstrap-project", str(project_path())])
        cmd_sync, data_sync, mode = run_with_mcp_fallback(
            mcp_tool="sync_project",
            mcp_payload={"project_id": project_id(), "mode": "incremental", "force": False},
            cli_args=["sync", project_id()],
        )
    except Exception as exc:  # noqa: BLE001
        fail(str(exc))
        return 1

    data_root = data_sync.get("data", data_sync)
    result = data_root.get("result", {})
    failed_docs = int(result.get("failed_docs", 0))
    indexed_docs = int(result.get("indexed_docs", 0))
    summary = f"Sync concluido via {mode}: indexed_docs={indexed_docs}, failed_docs={failed_docs}."
    next_step = "Use run_search.py para validar hits semanticos." if failed_docs == 0 else "Revise warnings/failed_docs antes de consultar."

    print_envelope(
        command=f"{cmd_init} && {cmd_bootstrap} && {cmd_sync}",
        summary=summary,
        next_step=next_step,
        data=data_root,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
