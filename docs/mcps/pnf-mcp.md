# MCP: pnf-mcp

## Objetivo

Expor o core do `pigmeu-never-forget` como MCP local para indexacao, retrieval e operacao do projeto.

## Local canônico

- codigo: `projects/pigmeu-never-forget/src/pigmeu_never_forget/mcp/`
- wrapper OpenCode: `opencode/scripts/pnf-mcp.sh`

## Superficies

- tools de sync, search, ask, stats, jobs e consolidacao
- resources para informacoes de projeto quando suportado pelo runtime

## Dependencias

- `projects/pigmeu-never-forget/src`
- config workspace via `PNF_CONFIG_PATH`
- runtime OpenCode conectado

## Variaveis de ambiente

- `PNF_REPO_PATH`
- `PNF_CONFIG_PATH`
- `PNF_PROJECT_ID`

## Execucao

```bash
PYTHONPATH=src python3 -m pigmeu_never_forget.mcp --config <config>
```

Ou via wrapper:

```bash
./opencode/scripts/pnf-mcp.sh
```

## Uso recomendado

- preferir MCP antes de CLI para agentes
- usar CLI como fallback em automacoes locais
- manter contratos alinhados com `docs/api-contracts.md`

## Documentos relacionados

- `projects/pigmeu-never-forget/docs/mcp-local.md`
- `projects/pigmeu-never-forget/docs/api-contracts.md`
- `projects/pigmeu-never-forget/docs/job-lifecycle.md`
