#!/usr/bin/env bash
# load-api-keys.sh — Loads rotated Mistral and Groq API keys into environment.
# Usage: source scripts/load-api-keys.sh
# Optionally set CREDENTIALS_CATALOG_DIR to override the default globals path.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CRED_ROTATE="python3 ${SCRIPT_DIR}/cred-rotate.py"

# Advance cursor and get active key for each provider
MISTRAL_KEY="$($CRED_ROTATE next mistral)"
GROQ_KEY="$($CRED_ROTATE next groq)"

if [[ -z "${MISTRAL_KEY}" || -z "${GROQ_KEY}" ]]; then
  echo "Erro: falha ao obter chaves atraves do cred-rotate.py" >&2
  exit 1
fi

export MISTRAL_API_KEY="${MISTRAL_KEY}"
export GROQ_API_KEY="${GROQ_KEY}"

# Show rotation status
$CRED_ROTATE status

echo "MISTRAL_API_KEY e GROQ_API_KEY exportadas para a sessao atual."
