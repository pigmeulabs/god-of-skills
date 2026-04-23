#!/usr/bin/env bash
set -euo pipefail

source /home/ubuntu/projects-workspace/god-of-skills/credentials-catalog/scripts/load-api-keys.sh
exec opencode "$@"
