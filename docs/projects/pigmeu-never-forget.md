# Projeto: pigmeu-never-forget

## Papel no monorepo

`pigmeu-never-forget` e o projeto central deste monorepo. Ele fornece:

- indexacao incremental local-first
- retrieval semantico e respostas grounded
- memoria consolidada por projeto
- MCP `pnf-mcp`
- MCP `pnf-session-memory`
- CLI e API HTTP local

## Local canônico

- `projects/pigmeu-never-forget/`

## Superficies principais

- CLI: `src/pigmeu_never_forget/cli.py`
- MCP core: `src/pigmeu_never_forget/mcp/`
- session memory: `src/pigmeu_never_forget/session_memory/`
- docs tecnicos: `projects/pigmeu-never-forget/docs/`

## Documentos relacionados

- `projects/pigmeu-never-forget/README.md`
- `projects/pigmeu-never-forget/docs/arquitetura.md`
- `projects/pigmeu-never-forget/docs/api-contracts.md`
- `projects/pigmeu-never-forget/docs/job-lifecycle.md`
- `../mcps/pnf-mcp.md`
- `../mcps/pnf-session-memory.md`
