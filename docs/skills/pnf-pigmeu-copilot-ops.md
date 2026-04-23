# Skill: pnf-pigmeu-copilot-ops

## Objetivo

Automatizar bootstrap, sincronizacao e consulta do projeto `pigmeu-copilot` usando o core do `pigmeu-never-forget`.

## Local canônico

- `skills/pnf-pigmeu-copilot-ops/`

## Escopo

- `ensure_bootstrap`
- `run_sync`
- `run_search`
- `run_ask`
- `run_stats`

## Dependencias

- projeto canonico: `projects/pigmeu-never-forget/`
- config OpenCode ou `PNF_CONFIG_PATH`
- workspace contendo o projeto `pigmeu-copilot`

## Comportamento

- usa `project_id=pigmeu-copilot` por padrao
- tenta MCP local primeiro
- faz fallback automatico para CLI
- retorna envelope com:
  - `command_executed`
  - `summary`
  - `next_step`
  - `data` ou `error`

## Variaveis de ambiente

- `PNF_REPO_PATH`
- `PNF_PROJECT_PATH`
- `PNF_PROJECT_ID`
- `PNF_CONFIG_PATH`
- `PNF_PREFER_MCP`

## Scripts

- `scripts/ensure_bootstrap.py`
- `scripts/run_sync.py`
- `scripts/run_search.py`
- `scripts/run_ask.py`
- `scripts/run_stats.py`
- `scripts/common.py`

## Fluxo recomendado

1. bootstrap
2. sync
3. search ou ask
4. stats

## Documentos relacionados

- `skills/pnf-pigmeu-copilot-ops/SKILL.md`
- `skills/pnf-pigmeu-copilot-ops/references/workflow.md`
- `skills/pnf-pigmeu-copilot-ops/references/error-playbook.md`
- `projects/pigmeu-never-forget/docs/api-contracts.md`
