"""Module entrypoint for local MCP server."""

from __future__ import annotations

import argparse

from pigmeu_never_forget.mcp.server import run_stdio_server


def main() -> int:
    parser = argparse.ArgumentParser(prog="pnf-mcp")
    parser.add_argument("--config", help="Optional workspace config path.")
    args = parser.parse_args()
    run_stdio_server(config_path=args.config)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

