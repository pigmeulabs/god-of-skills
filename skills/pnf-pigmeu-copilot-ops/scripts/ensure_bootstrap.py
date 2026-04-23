#!/usr/bin/env python3
"""Idempotent bootstrap for workspace and pigmeu-copilot project."""

from __future__ import annotations

from common import fail, print_envelope, project_path, run_pnf_cli


def main() -> int:
    try:
        cmd_init, data_init = run_pnf_cli(["init-workspace"])
        cmd_bootstrap, data_bootstrap = run_pnf_cli(["bootstrap-project", str(project_path())])
    except Exception as exc:  # noqa: BLE001
        fail(str(exc))
        return 1

    print_envelope(
        command=f"{cmd_init} && {cmd_bootstrap}",
        summary="Workspace e projeto garantidos com sucesso (idempotente).",
        next_step="Execute run_sync.py para indexar ou atualizar a base vetorizada.",
        data={
            "workspace": data_init,
            "project": data_bootstrap,
        },
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

