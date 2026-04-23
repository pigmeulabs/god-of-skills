# Pipeline Codex-Ready (Implementação)

Este documento consolida a execução da pipeline em 8 etapas para uso com Codex, ancorada nos documentos normativos:

* Hub: `docs/arquitetura.md`
* Persistência: `docs/data-model.md`
* Superfícies: `docs/api-contracts.md`
* Concorrência/recuperação: `docs/job-lifecycle.md`

## Skills por etapa

* `python-expert`: estrutura Python, tipos, stores, jobs, API, testes, hardening.
* `rag-architect`: ingestão, chunking, embeddings, retrieval, memória e consolidação.

Ordem recomendada em tarefas mistas:
1. `rag-architect` decide pipeline e critérios.
2. `python-expert` implementa os componentes.

## Estado atual por etapa

### Etapa 0 — Bootstrap e contratos de configuração
Status: implementada.

Entregas:
* pacote Python com `pyproject.toml`
* loaders de config e defaults
* modelos e enums base

### Etapa 1 — Persistência local e lifecycle
Status: implementada (funcional inicial).

Entregas:
* `.rag/`, `state.db`, `memory.db`
* migrations forward-only
* `WorkspaceService`, `ProjectService`
* `job_runs` e `project_locks`

### Etapa 2 — Ingestão, parsing e diff incremental
Status: implementada (funcional inicial).

Entregas:
* discovery por include/exclude
* parsing e normalização para Markdown com `markdownify`
* `source_hash`, `content_hash`, checkpoints
* diff com `new/modified/unchanged/deleted/renamed`
* reentrada segura após falha parcial

### Etapa 3 — Chunking, embeddings e vetor store
Status: implementada (funcional inicial).

Entregas:
* análise heurística e chunking híbrido
* embeddings determinísticos locais
* mirror local em `vector_index.json`
* backend Qdrant inicial com fallback local

### Etapa 4 — Knowledge index, summaries e memória base
Status: implementada (funcional inicial).

Entregas:
* summaries por documento
* `project_summary`
* entidades, aliases e facts compactos

### Etapa 5 — Retrieval, ask e resposta RAG
Status: implementada (funcional inicial).

Entregas:
* summary-first retrieval
* query rewrite com aliases
* contexto com budget
* resposta grounded com `sources`
* persistência em `query_history` e `api_calls`

### Etapa 6 — Consolidação AutoDream-like
Status: implementada (funcional inicial).

Entregas:
* `MemoryConsolidationService`
* `prune` de duplicatas
* refresh de summary
* auditoria básica

### Etapa 7 — CLI, API HTTP e MCP
Status: parcial.

Entregas:
* CLI operacional (`sync`, `search`, `ask`, `consolidate`, `stats`)
* MCP local v1.1 (tools e resources principais, incluindo `index_text`, `consolidate_project`, `get_job_status`)
* Correlacao por `request_id` e logging MCP em `log_events`
* HTTP local v1 (FastAPI) com envelopes padronizados

Pendente:
* ampliar MCP para recursos adicionais de auditoria e jobs agregados
* fortalecer semântica assíncrona/202 para jobs longos no HTTP

### Etapa 8 — Observabilidade, credenciais e hardening
Status: parcial.

Entregas:
* hardening pontual (consistência incremental, fallback vetorial, limites `top_k`)

Pendente:
* logs estruturados completos
* retries com jitter e correlação
* rotação de chave/retenção/recovery avançado

## Pacotes de trabalho recomendados

* Pacote A: Etapas 0 + 1
* Pacote B: Etapas 2 + 3
* Pacote C: Etapas 4 + 5
* Pacote D: Etapas 6 + 7 + 8

## Critérios de pronto por pacote

### Pacote A
* bootstrap workspace/projeto funcional
* migrations aplicadas
* lock exclusivo validado

### Pacote B
* indexação inicial e incremental
* rename/exclusão/falha parcial cobertos
* ingestão até vetor store operacional

### Pacote C
* summaries gerados
* retrieval coerente
* `ask` grounded com fontes

### Pacote D
* consolidação incremental com auditoria
* adaptadores externos finos
* operação resiliente e observável

## Comandos de verificação

```bash
pytest -q
PYTHONPATH=src python3 -m pigmeu_never_forget.cli sync <project>
PYTHONPATH=src python3 -m pigmeu_never_forget.cli search <project> "query" --top-k 5
PYTHONPATH=src python3 -m pigmeu_never_forget.cli ask <project> "pergunta" --top-k 5
```

## Referências

* `README.md`
* `docs/implementation-status.md`
* `docs/arquitetura.md`
* `docs/data-model.md`
* `docs/api-contracts.md`
* `docs/job-lifecycle.md`
