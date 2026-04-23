# AGENTS.md

## Scope

- Use `god-of-skills` como repositório canônico para skills, MCPs, wrappers OpenCode e `pigmeu-never-forget`.
- Considere `.opencode/` apenas como instalação de runtime.
- Faça mudanças aqui primeiro e sincronize depois.

## Working rules

- Mantenha respostas curtas e densas em informação.
- Prefira referenciar arquivos do monorepo em vez de repetir conteúdo longo.
- Se mudar comportamento de skill, MCP, CLI ou fluxo operacional, atualize os docs em `docs/`.
- Preserve instruções operacionais detalhadas em arquivos satélite; mantenha este arquivo enxuto.

## Canonical map

- `projects/pigmeu-never-forget/`: core do sistema e documentação técnica
- `skills/`: skills customizadas
- `mcps/`: documentação e contratos operacionais dos MCPs
- `opencode/scripts/`: wrappers canônicos para registrar MCPs
- `docs/`: visão consolidada do monorepo

## Runtime sync

- OpenCode usa `.opencode/opencode.json` e `.opencode/scripts/`.
- Os caminhos desse runtime devem apontar para `god-of-skills/projects/pigmeu-never-forget`.
- Ao alterar skill ou MCP canônico, confirme se o espelho em `.opencode/` ainda está alinhado.

## Session memory

- Após cada resposta do agente, registrar a interação com `pnf-session-memory.record_response` ou com a skill `pnf-session-memory-ops`.
- Finalizar e arquivar a sessão no encerramento.
- Guardar sessões em `projects/pigmeu-never-forget/docs/memories/sessions/<stem>/<stem>.md`.
