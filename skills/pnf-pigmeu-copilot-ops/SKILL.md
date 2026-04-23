---
name: pnf-pigmeu-copilot-ops
description: Automatiza bootstrap, sync, search, ask e stats do projeto pigmeu-copilot usando pigmeu-never-forget. Use quando precisar indexar o plugin, atualizar a base vetorizada, consultar fatos do codigo/documentacao, ou diagnosticar saude da base local.
---

# PNF Pigmeu Copilot Ops

Execute operacoes manuais e seguras para construir e consultar a base de conhecimento vetorizada do `pigmeu-copilot`.

## Fluxo padrao

1. Garantir bootstrap:
```bash
python3 scripts/ensure_bootstrap.py
```
2. Sincronizar e indexar:
```bash
python3 scripts/run_sync.py
```
3. Buscar contexto:
```bash
python3 scripts/run_search.py "sua query" --top-k 8
```
4. Perguntar com grounding:
```bash
python3 scripts/run_ask.py "sua pergunta" --top-k 6
```
5. Validar saude:
```bash
python3 scripts/run_stats.py
```

## Comportamento operacional

* Operar sempre com `project_id=pigmeu-copilot` (override por `PNF_PROJECT_ID`).
* Rodar em modo manual, sem agendamento.
* Preferir chamadas MCP locais (`mcp.local_call`) e usar CLI como fallback automatico.
* Retornar sempre JSON com:
  * `command_executed`
  * `summary`
  * `next_step`
  * `data` (ou `error`)

## Configuracao por ambiente

* `PNF_REPO_PATH`: caminho do repositório `pigmeu-never-forget`.
* `PNF_PROJECT_PATH`: caminho do projeto alvo (`pigmeu-copilot`).
* `PNF_PROJECT_ID`: id do projeto no workspace.
* `PNF_PREFER_MCP`: `1` (default) para priorizar MCP; `0` para forcar CLI.

Se variaveis nao forem fornecidas, usar defaults locais do workspace atual.

## Referencias

* Fluxo operacional: `references/workflow.md`
* Tratamento de erros: `references/error-playbook.md`
