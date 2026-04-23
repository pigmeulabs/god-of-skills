# Skill `pnf-pigmeu-copilot-ops`

Skill operacional para automacao manual de `bootstrap/sync/search/ask/stats` do projeto `pigmeu-copilot`.
Quando instalada dentro de `.opencode/skills/`, ela detecta automaticamente o projeto atual.

## Fonte canônica

Esta documentação legada complementa a documentação central do monorepo:

* `/home/ubuntu/projects-workspace/god-of-skills/docs/skills/pnf-pigmeu-copilot-ops.md`

## Local da skill

```text
${CODEX_HOME:-$HOME/.codex}/skills/pnf-pigmeu-copilot-ops
```

## Scripts principais

* `scripts/ensure_bootstrap.py`
* `scripts/run_sync.py`
* `scripts/run_search.py`
* `scripts/run_ask.py`
* `scripts/run_stats.py`

## Uso rapido

```bash
cd ${CODEX_HOME:-$HOME/.codex}/skills/pnf-pigmeu-copilot-ops
python3 scripts/ensure_bootstrap.py
python3 scripts/run_sync.py
python3 scripts/run_search.py "como funciona autenticacao?"
python3 scripts/run_ask.py "Explique o fluxo de artigos no plugin"
python3 scripts/run_stats.py
```

## Contrato de saida dos scripts

Todos os scripts retornam JSON com:

* `command_executed`
* `summary`
* `next_step`
* `data` (sucesso) ou `error` (falha)

Os wrappers da skill usam estrategia **MCP primeiro, CLI fallback** automaticamente.

## Variaveis de ambiente

* `PNF_REPO_PATH` (default: `/home/ubuntu/projects-workspace/god-of-skills/projects/pigmeu-never-forget`)
* `PNF_PROJECT_PATH` (default: auto detectado via caminho da skill em `.opencode`)
* `PNF_PROJECT_ID` (default: nome do diretório do projeto detectado automaticamente)
* `PNF_PREFER_MCP` (default: `1`; use `0` para forcar CLI)

## Erros comuns

Referenciar `references/error-playbook.md` da skill para tratamento de:

* `PROJECT_NOT_FOUND`
* `PROJECT_LOCKED`
* `VECTOR_STORE_ERROR`
