# OpenCode Runtime

## Objetivo

Explicar como o runtime do OpenCode consome os artefatos canonicos de `god-of-skills`.

## Componentes

- Config global: `/home/ubuntu/.config/opencode/opencode.json`
- Config: `/home/ubuntu/projects-workspace/.opencode/opencode.json`
- Wrappers instalados:
  - `/home/ubuntu/projects-workspace/.opencode/scripts/pnf-mcp.sh`
  - `/home/ubuntu/projects-workspace/.opencode/scripts/pnf-session-mcp.sh`
  - `/home/ubuntu/projects-workspace/.opencode/scripts/opencode-rotated.sh`
- Fonte canonica dos wrappers:
  - `opencode/scripts/pnf-mcp.sh`
  - `opencode/scripts/pnf-session-mcp.sh`
  - `opencode/scripts/opencode-rotated.sh`

## Regra de caminho

Todos os wrappers e a configuracao do runtime devem apontar para:

`/home/ubuntu/projects-workspace/god-of-skills/projects/pigmeu-never-forget`

## MCPs ativos

- `pnf-mcp`
  - indexacao, busca, ask, stats, jobs, consolidacao
- `pnf-session-memory`
  - sessoes incrementais, rollover, finalizacao e arquivamento
- `opencode-rotated.sh`
  - carrega Mistral/Groq rotacionados antes de abrir o OpenCode

## Providers globais

O config global do OpenCode habilita `mistral` e `groq` em `provider`, para que aparecam no seletor de modelos em qualquer workspace.

## Verificacao

```bash
opencode mcp list
```

Estado esperado:

- `pnf-mcp connected`
- `pnf-session-memory connected`

## Sincronizacao operacional

Quando uma skill ou um wrapper mudar no monorepo:

1. atualize o artefato canonico em `god-of-skills`
2. sincronize o espelho correspondente em `.opencode/`
3. rode `opencode mcp list`
