# Skill: pnf-session-memory-ops

## Objetivo

Persistir a sessao incrementalmente em markdown e arquivar a sessao finalizada no `pigmeu-never-forget`.

## Local canônico

- `skills/pnf-session-memory-ops/`

## Escopo

- iniciar sessao
- registrar resposta do agente
- atualizar metricas
- verificar status
- finalizar sessao
- arquivar sessao
- rollover de sessao inativa

## Dependencias

- MCP `pnf-session-memory`
- projeto canonico `projects/pigmeu-never-forget/`
- config OpenCode via `PNF_CONFIG_PATH`

## Comportamento

- mantem um arquivo por sessao em `projects/pigmeu-never-forget/docs/memories/sessions/<stem>/<stem>.md`
- usa `record_response` como fluxo principal por turno
- trata sessoes com mais de 8 horas sem atividade como stale
- arquiva a sessao finalizada no PNF para memoria de longo prazo
- salva metricas indisponiveis como `null` ou `unknown`

## Variaveis de ambiente

- `PNF_REPO_PATH`
- `PNF_CONFIG_PATH`
- `PNF_SESSION_PREFER_MCP`
- `PNF_SESSION_ARCHIVE_PROJECT_ID`

## Scripts

- `scripts/ensure_session.py`
- `scripts/record_response.py`
- `scripts/update_metrics.py`
- `scripts/status.py`
- `scripts/finalize_session.py`
- `scripts/archive_session.py`
- `scripts/common.py`

## Fluxo recomendado

1. `ensure_session`
2. `record_response` a cada resposta
3. `status` quando necessario
4. `finalize_session` no encerramento

## Documentos relacionados

- `skills/pnf-session-memory-ops/SKILL.md`
- `skills/pnf-session-memory-ops/references/workflow.md`
- `skills/pnf-session-memory-ops/references/error-playbook.md`
- `projects/pigmeu-never-forget/docs/memories/sessions/README.md`
