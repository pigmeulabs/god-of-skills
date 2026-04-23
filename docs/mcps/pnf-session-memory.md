# MCP: pnf-session-memory

## Objetivo

Persistir sessoes incrementais de agentes em markdown e arquivar sessoes finalizadas no `pigmeu-never-forget`.

## Local canônico

- codigo: `projects/pigmeu-never-forget/src/pigmeu_never_forget/session_memory/`
- wrapper OpenCode: `opencode/scripts/pnf-session-mcp.sh`

## Tools principais

- `start_session`
- `append_turn`
- `update_metrics`
- `record_response`
- `finalize_session`
- `archive_session`
- `rollover_stale_sessions`
- `get_session_status`
- `latest_session`

## Comportamento

- grava em `projects/pigmeu-never-forget/docs/memories/sessions/<stem>/<stem>.md`
- um arquivo por sessao
- atualizacao incremental no mesmo arquivo
- finalizacao explicita ou rollover apos 8 horas
- arquivamento da sessao finalizada no PNF

## Variaveis de ambiente

- `PNF_REPO_PATH`
- `PNF_CONFIG_PATH`
- `PNF_SESSION_ARCHIVE_PROJECT_ID`

## Execucao

```bash
PYTHONPATH=src python3 -m pigmeu_never_forget.session_memory.server --config <config>
```

Ou via wrapper:

```bash
./opencode/scripts/pnf-session-mcp.sh
```

## Documentos relacionados

- `projects/pigmeu-never-forget/docs/memories/sessions/README.md`
- `projects/pigmeu-never-forget/docs/api-contracts.md`
- `docs/skills/pnf-session-memory-ops.md`
