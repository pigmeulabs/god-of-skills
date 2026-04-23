"""Local helper to call MCP adapter tools without transport."""

from __future__ import annotations

import argparse
import json
from typing import Any

from pigmeu_never_forget.mcp.adapter import PNFMCPAdapter


def _parse_json(value: str | None, default: dict[str, Any] | None = None) -> dict[str, Any]:
    if not value:
        return default or {}
    parsed = json.loads(value)
    if not isinstance(parsed, dict):
        raise ValueError("Payload JSON must be an object.")
    return parsed


def _dispatch(adapter: PNFMCPAdapter, tool: str, payload: dict[str, Any]) -> dict[str, Any]:
    mapping = {
        "list_projects": adapter.list_projects,
        "sync_project": adapter.sync_project,
        "index_text": adapter.index_text,
        "search_project": adapter.search_project,
        "ask_project": adapter.ask_project,
        "get_project_stats": adapter.get_project_stats,
        "consolidate_project": adapter.consolidate_project,
        "get_job_status": adapter.get_job_status,
    }
    fn = mapping.get(tool)
    if fn is None:
        raise ValueError(f"Unsupported tool: {tool}")
    return fn(**payload)


def main() -> int:
    parser = argparse.ArgumentParser(prog="pnf-mcp-call")
    parser.add_argument("tool", help="Tool name.")
    parser.add_argument("--payload", help="JSON object payload.")
    parser.add_argument("--config", help="Optional workspace config path.")
    args = parser.parse_args()

    payload = _parse_json(args.payload, default={})
    adapter = PNFMCPAdapter(config_path=args.config)
    result = _dispatch(adapter, tool=args.tool, payload=payload)
    print(json.dumps(result, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

