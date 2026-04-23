# Status da Implementação

Este documento registra o que já foi implementado no repositório em relação à arquitetura definida em [arquitetura.md](arquitetura.md).

## Diagrama consolidado

* Fonte Mermaid: `docs/diagrams/fluxo-funcionalidades.mmd`
* Export PNG: `docs/diagrams/fluxo-funcionalidades.png`

## Implementado nesta rodada

### Fundação do projeto Python

* `pyproject.toml` com pacote instalável e CLI `pnf`
* pacote `src/pigmeu_never_forget/`
* bootstrap de aplicação em `app.py`

### Tipos e erros base

* enums de `job`, `lock`, `document` e `error code`
* dataclasses normativas de domínio:
  `ProjectContext`, `SourceDocument`, `ChunkRecord`, `EmbeddingRecord`, `IndexJobResult`
* tipos esqueleto para as próximas fases:
  `AnalysisResult`, `RetrievalHit`, `AnswerResult`, `ConsolidationPlan`, `ConsolidationResult`
* `AppError` estruturado alinhado com `docs/api-contracts.md`

### Configuração e bootstrap

* defaults de workspace, projeto e prompts
* loader YAML com merge recursivo
* resolução de paths de workspace e projeto
* geração automática de `_workspace/config.yaml`, `_workspace/credentials.yaml`, `.rag/project.yaml` e `.rag/prompts.yaml`

### Persistência local

* migrations forward-only para `state.db` e `memory.db`
* bootstrap de schema conforme `docs/data-model.md`
* utilitários SQLite com transação e `foreign_keys=on`
* `registry.db` com tabela `projects`

### Serviços implementados

* `WorkspaceService`
  * inicialização do workspace
  * descoberta de projetos
  * bootstrap automático de `.rag/`
* `ProjectService`
  * inicialização de projeto
  * aplicação de migrations
  * geração de estrutura local
* `JobService`
  * criação e transição de jobs
  * heartbeat
  * finalização
  * lock exclusivo por projeto
  * recuperação de jobs com heartbeat expirado

### Ingestão incremental (Etapa 2 funcional)

* `IngestionService` com:
  * descoberta de arquivos elegíveis por `include_paths` e `exclude_patterns`
  * suporte inicial aos formatos: `txt`, `md`, `pdf`, `docx`, `html`, `json`, `csv`, `py`, `js`, `ts`
    e imagens (`png`, `jpg`, `jpeg`, `gif`, `webp`, `bmp`, `tiff`, `svg`)
  * normalização para **Markdown** usando `markdownify` como conversor principal
  * normalização por formato para `json`, `csv` e `html`
  * extração para `pdf` via `pypdf` quando disponível
  * extração para `docx` via `python-docx` quando disponível
  * extração de metadados de imagem via `Pillow` quando disponível
  * fallback para stubs markdownificados quando parser específico não estiver disponível
  * snapshots com `source_hash`, `content_hash` e `parser_version`
  * diff incremental com categorias `new`, `modified`, `unchanged`, `deleted`, `renamed`
  * detecção de rename por similaridade de `content_hash`
  * persistência de checkpoints em `file_checkpoints`
* Reconciliação de falha parcial:
  * listagem de `chunks` ativos sem `qdrant_point_id`
  * marcação de confirmação vetorial por `chunk_id`

### Etapa 3 (versão funcional inicial)

* `AnalysisService` heurístico com classificação de documento e recomendação de chunking
* `ChunkingService` com divisão por heading/parágrafo e janela com overlap
* `EmbeddingService` determinístico local para desenvolvimento e testes
* `VectorStoreService` funcional com mirror local em `.rag/cache/vector_index.json`:
  * upsert de vetores e payload por chunk
  * busca por similaridade cosseno
  * remoção por `doc_id`
* backend Qdrant inicial:
  * seleção por `project.settings.storage.vector_backend=qdrant`
  * tentativa de upsert/search/delete remoto por coleção
  * criação automática da collection com distância cosseno
  * fallback para mirror local se cliente/servidor indisponível
* `IndexingService` orquestrando:
  * diff incremental -> reindexação seletiva
  * análise -> chunking -> embedding -> persistência vetorial
  * atualização de `documents` e `chunks`
  * marcação lógica de exclusão e desativação de chunks antigos
  * correção de consistência incremental:
    * checkpoint não é persistido para arquivos que falharam na indexação
    * em rename, o caminho antigo só é desativado após indexação bem-sucedida do novo caminho

### Etapa 4 e 5 (versão funcional inicial)

* `MemoryIndexService`:
  * gera `summary_short` e `summary_full` por documento
  * extrai tópicos básicos
  * popula `entities`, `entity_aliases` e `memory_facts`
  * atualiza `project_summary` com `active_facts_compact_json`
* `RetrievalService`:
  * busca vetorial operacional
  * query rewrite leve com aliases
  * montagem de contexto summary-first (`summary_short`, facts e vector hits)
  * persistência de `query_history` e `api_calls`
* `AnswerService`:
  * resposta grounded com `sources`
  * estimativa de uso de contexto e latência

### Etapa 6 (versão funcional inicial)

* `MemoryConsolidationService.execute` implementado com:
  * `prune` de fatos duplicados
  * refresh de `project_summary`
  * auditoria básica em `consolidation_audit`

### Etapa 7 (CLI operacional inicial)

* comandos adicionados:
  * `sync`
  * `index-text`
  * `search`
  * `ask`
  * `consolidate`
  * `stats`
  * `job-status`
  * `mcp-serve`
  * `api-serve`
* HTTP local (FastAPI) v1 implementado:
  * endpoints de `health`, `projects`, `sync`, `index-text`, `search`, `ask`, `consolidate`, `stats`, `jobs/{job_id}`
  * envelope de sucesso/erro alinhado com `docs/api-contracts.md`
  * suporte a `X-Request-Id` com geração automática
* MCP local v1 implementado:
  * tools: `list_projects`, `sync_project`, `index_text`, `search_project`, `ask_project`, `get_project_stats`, `consolidate_project`, `get_job_status`
  * resources: `rag://projects`, `rag://project/{project_id}/summary`, `rag://project/{project_id}/stats`, `rag://project/{project_id}/jobs/{job_id}`
  * envelope de erro/sucesso padronizado para `code`, `message`, `retryable`, `details`
  * suporte a `request_id` opcional com geracao automatica para correlacao
  * logging estruturado em `log_events` (service=`mcp`, trace_id=`request_id`)
  * utilitario local `mcp.local_call` para chamadas de tools sem transporte (usado por wrappers)

### Hardening aplicado

* `VectorStoreService.search(top_k=0)` retorna lista vazia
* `IndexJobResult.indexed_docs` reflete docs efetivamente atualizados no ciclo
* compatibilidade YAML unificada em `utils/yaml_compat.py` (PyYAML + fallback local)
* integração operacional OpenCode:
  * skill `pnf-pigmeu-copilot-ops` sincronizada para `.opencode/skills/`
  * MCP `pnf-mcp` registrado em `.opencode/opencode.json`
  * instruções de uso centralizadas em `.opencode/instructions/pnf-system.md`
* memória de sessão:
  * MCP `pnf-session-memory` registrado em `.opencode/opencode.json`
  * skill `pnf-session-memory-ops` sincronizada para `.opencode/skills/`
  * sessões gravadas em `docs/memories/sessions/<stem>/<stem>.md`
* monorepo canônico:
  * `god-of-skills/` definido como fonte principal da verdade
  * projeto `pigmeu-never-forget` movido para `god-of-skills/projects/pigmeu-never-forget/`
  * documentação central de skills e MCPs criada em `god-of-skills/docs/`

### Testes automatizados

* config default e merge
* rejeição de config inválida
* bootstrap de workspace
* bootstrap de projeto com schema criado
* lock exclusivo por projeto
* incremental sem mudança
* rename sem duplicidade indevida
* exclusão de arquivo no diff
* reconciliação de falha parcial de vetor
* normalização markdown de `html`, `json`, `csv`, `pdf` e imagem
* pipeline de indexação da Etapa 3 com busca vetorial local
* regressões de consistência: checkpoint em falha e desativação correta no rename
* runtime integrado: `sync/search/ask/stats/consolidate`
* `top_k=0` em busca vetorial
* backend Qdrant:
  * uso remoto quando cliente disponível
  * fallback local quando cliente indisponível
* contratos MCP:
  * envelope de sucesso com `status/data/meta`
  * mapeamento de erros para `PROJECT_NOT_FOUND` e `INTERNAL_ERROR`
* memória de sessão:
  * gravação incremental do markdown canônico por sessão
  * rollover por inatividade
  * arquivamento em `pnf-session-memory`

## Ainda não implementado

* FAISS mirror real
* sumarização/extração via LLM (hoje heurística/local)
* consolidação AutoDream-like avançada (hoje versão inicial de prune/refresh)
* observabilidade completa e rotação de credenciais em produção

## Mapeamento para a pipeline

* Etapa 0: implementada
* Etapa 1: implementada em versão funcional inicial
* Etapa 2: implementada em versão funcional inicial
* Etapa 3: implementada em versão funcional inicial (inclui backend Qdrant com fallback)
* Etapa 4: implementada em versão funcional inicial
* Etapa 5: implementada em versão funcional inicial
* Etapa 6: implementada em versão funcional inicial
* Etapa 7: implementada em versão funcional inicial (CLI + MCP local v1.1 + HTTP local v1)
* Etapa 8: parcialmente implementada (hardening pontual)

## Próximo melhor passo

Concluir produção das próximas superfícies:

* robustecer integração Qdrant (filtros, healthcheck e retries) e implementar FAISS real
* endurecer HTTP para auth/token, validações de payload e semântica assíncrona de jobs
* observabilidade operacional e segurança avançada
