# Setup OpenCode (Skills + MCP)

Este guia registra a configuração operacional do OpenCode para usar `pigmeu-never-forget` no workspace.

## Fonte da verdade

O runtime usa `.opencode/`, mas a manutenção canônica acontece em:

* `/home/ubuntu/projects-workspace/god-of-skills`
* wrappers canônicos: `/home/ubuntu/projects-workspace/god-of-skills/opencode/scripts/`
* skills canônicas: `/home/ubuntu/projects-workspace/god-of-skills/skills/`

## Arquivos de configuração

* Workspace OpenCode: `/home/ubuntu/projects-workspace/.opencode/opencode.json`
* Instruções OpenCode: `/home/ubuntu/projects-workspace/.opencode/instructions/pnf-system.md`
* Config PNF para workspace: `/home/ubuntu/projects-workspace/.opencode/pnf-workspace-config.yaml`
* Script MCP local instalado: `/home/ubuntu/projects-workspace/.opencode/scripts/pnf-mcp.sh`
* Script MCP de sessão instalado: `/home/ubuntu/projects-workspace/.opencode/scripts/pnf-session-mcp.sh`
* Wrapper OpenCode com chaves rotacionadas: `/home/ubuntu/projects-workspace/.opencode/scripts/opencode-rotated.sh`
* Script MCP local canônico: `/home/ubuntu/projects-workspace/god-of-skills/opencode/scripts/pnf-mcp.sh`
* Script MCP de sessão canônico: `/home/ubuntu/projects-workspace/god-of-skills/opencode/scripts/pnf-session-mcp.sh`
* Wrapper OpenCode canônico: `/home/ubuntu/projects-workspace/god-of-skills/opencode/scripts/opencode-rotated.sh`

## Skill ativada no workspace

Skill operacional copiada para:

* `/home/ubuntu/projects-workspace/.opencode/skills/pnf-pigmeu-copilot-ops/`
* `/home/ubuntu/projects-workspace/.opencode/skills/pnf-session-memory-ops/`
* `/home/ubuntu/projects-workspace/.opencode/skills/credentials-catalog/`
* `/home/ubuntu/projects-workspace/.opencode/skills/agent-skill-creator` (symlink local)

Fonte canônica:

* `/home/ubuntu/projects-workspace/god-of-skills/skills/pnf-pigmeu-copilot-ops/`
* `/home/ubuntu/projects-workspace/god-of-skills/skills/pnf-session-memory-ops/`

Conteúdo principal:

* `SKILL.md`
* `scripts/run_sync.py`, `run_search.py`, `run_ask.py`, `run_stats.py`, `ensure_bootstrap.py`
* `references/workflow.md`, `references/error-playbook.md`

Observacoes:

* `credentials-catalog` ja estava presente no runtime local.
* `agent-skill-creator` foi exposto no runtime via symlink para `/home/ubuntu/projects-workspace/skills/agent-skill-creator`.
* Nao foi encontrado um pacote local identificavel chamado `skill-installer` neste workspace.

## MCP ativado

Servidor registrado no OpenCode:

* `pnf-mcp` (comando: `/home/ubuntu/projects-workspace/.opencode/scripts/pnf-mcp.sh`)
* `pnf-session-memory` (comando: `/home/ubuntu/projects-workspace/.opencode/scripts/pnf-session-mcp.sh`)

Validação:

```bash
cd /home/ubuntu/projects-workspace
opencode mcp list
```

Estado esperado: `pnf-mcp connected` e `pnf-session-memory connected`.

## API HTTP local

Para uso via HTTP no ambiente local:

```bash
cd /home/ubuntu/projects-workspace/god-of-skills/projects/pigmeu-never-forget
PYTHONPATH=src python3 -m pigmeu_never_forget.cli api-serve --host 127.0.0.1 --port 8787
```

## Dependências

Dependência Python instalada para o servidor MCP:

```bash
python3 -m pip install --user --break-system-packages mcp
```

## Observações

* O `pnf-mcp` usa `PYTHONPATH=/home/ubuntu/projects-workspace/god-of-skills/projects/pigmeu-never-forget/src`.
* O `pnf-mcp` opera com config apontando para `projects-workspace` como root.
* A instrução `.opencode/instructions/pnf-system.md` prioriza uso de MCP + skill local.
* O `pnf-session-memory` grava `docs/memories/sessions/<stem>/<stem>.md` e arquiva no projeto `pigmeu-never-forget`.
