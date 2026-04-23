#!/usr/bin/env bash
set -euo pipefail

PNF_REPO_PATH="${PNF_REPO_PATH:-/home/ubuntu/projects-workspace/god-of-skills/projects/pigmeu-never-forget}"
PNF_CONFIG_PATH="${PNF_CONFIG_PATH:-/home/ubuntu/projects-workspace/.opencode/pnf-workspace-config.yaml}"

export PYTHONPATH="${PNF_REPO_PATH}/src${PYTHONPATH:+:${PYTHONPATH}}"

exec python3 -m pigmeu_never_forget.session_memory.server --config "${PNF_CONFIG_PATH}"
