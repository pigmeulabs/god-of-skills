# God of Skills

Monorepo canônico para skills, MCPs, operação OpenCode e o projeto `pigmeu-never-forget`.

## Objetivo

Este repositório é a fonte principal da verdade para:

- código do `pigmeu-never-forget`
- skills operacionais e especializadas criadas no workspace
- wrappers e configuração de MCPs locais
- documentação de arquitetura, operação e integração

As instalações em `.opencode/` são espelhos de runtime. Alterações devem nascer aqui e depois ser sincronizadas para o ambiente de execução.

## Estrutura

- `projects/pigmeu-never-forget/`: código-fonte principal, testes, CLI, API, MCPs e documentação do projeto
- `skills/`: skills customizadas mantidas pelo time
- `mcps/`: documentação e manifestos operacionais dos MCPs locais
- `opencode/scripts/`: wrappers canônicos usados para registrar MCPs no OpenCode
- `docs/`: documentação central do monorepo

## Componentes principais

### Projeto

- `pigmeu-never-forget`
  - indexação local-first
  - busca vetorial e `ask`
  - consolidação de memória
  - MCP `pnf-mcp`
  - MCP `pnf-session-memory`

### Skills

- `pnf-pigmeu-copilot-ops`
  - bootstrap, sync, search, ask e stats do `pigmeu-copilot`
- `pnf-session-memory-ops`
  - persistência incremental de sessão, rollover por inatividade e arquivamento no PNF

## Fluxo de manutenção

1. Implementar e testar no monorepo `god-of-skills`.
2. Atualizar documentação central em `docs/`.
3. Sincronizar artefatos de runtime em `.opencode/` quando necessário.
4. Validar MCPs com `opencode mcp list`.

## Documentação

- [Fonte da verdade](docs/architecture/source-of-truth.md)
- [Operação OpenCode](docs/operations/opencode-runtime.md)
- [Projeto `pigmeu-never-forget`](docs/projects/pigmeu-never-forget.md)
- [Skill `pnf-pigmeu-copilot-ops`](docs/skills/pnf-pigmeu-copilot-ops.md)
- [Skill `pnf-session-memory-ops`](docs/skills/pnf-session-memory-ops.md)
- [MCP `pnf-mcp`](docs/mcps/pnf-mcp.md)
- [MCP `pnf-session-memory`](docs/mcps/pnf-session-memory.md)
- [README do projeto](projects/pigmeu-never-forget/README.md)
