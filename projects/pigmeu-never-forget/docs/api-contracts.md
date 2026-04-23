# Contratos de API e MCP

Este documento fecha as superfícies externas do sistema. HTTP e MCP são adaptadores do mesmo núcleo de serviços.

## Regras gerais

* Todas as rotas e tools que operam sobre dados devem ser `project-aware`.
* Operações potencialmente longas retornam `job_id`.
* Erros retornam payload estruturado.
* O modo inicial é single-user/local-first, mas a API já deve aceitar cabeçalho de correlação.

## Cabeçalhos HTTP

* `X-Request-Id`: opcional, ecoado na resposta.
* `X-Project-Id`: opcional apenas em rotas globais; obrigatório quando a rota não embute o projeto.
* `Authorization: Bearer <token>`: opcional na fase local, obrigatório quando a API for exposta fora da máquina local.

## Envelope de sucesso

```json
{
  "status": "ok",
  "data": {},
  "meta": {
    "project_id": "projeto-a",
    "request_id": "req_123"
  }
}
```

## Envelope de erro

```json
{
  "status": "error",
  "error": {
    "code": "PROJECT_NOT_FOUND",
    "message": "Projeto inexistente ou não registrado.",
    "retryable": false,
    "details": {}
  },
  "meta": {
    "request_id": "req_123"
  }
}
```

## Códigos de erro

* `PROJECT_NOT_FOUND`
* `PROJECT_LOCKED`
* `SESSION_NOT_FOUND`
* `INVALID_REQUEST`
* `PARSER_ERROR`
* `PROVIDER_RATE_LIMITED`
* `PROVIDER_UNAVAILABLE`
* `VECTOR_STORE_ERROR`
* `CONSOLIDATION_CONFLICT`
* `INTERNAL_ERROR`

## Endpoints HTTP

### `GET /projects`

Lista projetos descobertos e seu estado resumido.

### `POST /projects/discover`

Dispara descoberta global.

Resposta:

```json
{
  "status": "ok",
  "data": {
    "projects": [
      {"project_id": "projeto-a", "status": "ready"}
    ]
  }
}
```

### `POST /projects/{project_id}/sync`

Executa sincronização completa ou incremental.

Request:

```json
{
  "mode": "incremental",
  "force": false,
  "trigger": "manual"
}
```

Response síncrona curta:

```json
{
  "status": "ok",
  "data": {
    "job_id": "job_sync_001",
    "job_status": "running"
  }
}
```

### `POST /projects/{project_id}/index-text`

Indexa texto bruto sem arquivo físico.

Request:

```json
{
  "title": "observacao_operacional",
  "text": "conteudo livre",
  "source_type": "inline_text",
  "tags": ["manual"]
}
```

### `POST /projects/{project_id}/search`

Busca semântica sem geração final.

Request:

```json
{
  "query": "como funciona autenticacao?",
  "top_k": 8,
  "expand": false
}
```

Response:

```json
{
  "status": "ok",
  "data": {
    "hits": [
      {
        "doc_id": "doc_auth",
        "chunk_id": "chunk_004",
        "score": 0.83,
        "path": "docs/auth.md",
        "section": "JWT"
      }
    ]
  }
}
```

### `POST /projects/{project_id}/ask`

Faz query RAG com grounding.

Request:

```json
{
  "question": "Como o projeto lida com refresh token?",
  "top_k": 6,
  "allow_summary_only": true
}
```

Response:

```json
{
  "status": "ok",
  "data": {
    "answer_short": "O fluxo usa...",
    "sources": [
      {"doc_id": "doc_1", "chunk_id": "chunk_4", "path": "docs/auth.md"}
    ],
    "needs_expansion": false,
    "usage": {
      "context_tokens_est": 1450
    }
  }
}
```

### `POST /projects/{project_id}/consolidate`

Dispara consolidação incremental.

Request:

```json
{
  "mode": "incremental",
  "trigger": "manual"
}
```

### `GET /projects/{project_id}/stats`

Retorna contagens, estado do último sync e saúde resumida.

### `DELETE /projects/{project_id}/document`

Request:

```json
{
  "path": "docs/auth.md",
  "hard_delete": false
}
```

Regra: `hard_delete=true` é reservado a manutenção administrativa e exige auditoria explícita.

## Jobs longos

* `sync` e `consolidate` podem responder `202 Accepted`.
* Jobs devem poder ser consultados via `GET /projects/{project_id}/jobs/{job_id}`.
* A API deve refletir `queued`, `running`, `succeeded`, `failed`, `cancelled`.

## Contratos MCP

### Tools

* `list_projects(request_id?) -> {projects: [...]}`
* `sync_project(project_id, mode='incremental', force=false, request_id?) -> {job_id, status}`
* `index_text(project_id, title, text, source_type='inline_text', tags=[], request_id?) -> {doc_id, chunks_created}`
* `search_project(project_id, query, top_k=8, expand=false, request_id?) -> {hits: [...]}`
* `ask_project(project_id, question, top_k=6, allow_summary_only=true, request_id?) -> {answer_short, sources, needs_expansion}`
* `consolidate_project(project_id, mode='incremental', request_id?) -> {job_id, status}`
* `get_project_stats(project_id, request_id?) -> {stats: {...}}`
* `get_job_status(project_id, job_id, request_id?) -> {job: {...}}`

### Session memory tools

* `start_session(payload?, request_id?) -> {session_stem, status, ...}`
* `append_turn(payload?, request_id?) -> {session_stem, turn_count, ...}`
* `record_response(payload?, request_id?) -> {session, stale_finalized, latest_before_record}`
* `update_metrics(payload?, request_id?) -> {session_stem, token_totals, ...}`
* `finalize_session(payload?, request_id?) -> {session_stem, status, archive_result, ...}`
* `archive_session(payload?, request_id?) -> {session_stem, archive, ...}`
* `rollover_stale_sessions(payload?, request_id?) -> {processed, count}`
* `get_session_status(payload?, request_id?) -> {session_stem, status, ...}`
* `latest_session(request_id?) -> {session: {...}}`

### Resources

* `rag://projects`
* `rag://project/{project_id}/config`
* `rag://project/{project_id}/summary`
* `rag://project/{project_id}/stats`
* `rag://project/{project_id}/jobs/{job_id}`

## Idempotência

* `sync` com o mesmo estado de fontes não deve produzir novos chunks nem novas chamadas de embedding.
* `index-text` é idempotente apenas quando o chamador fornece a mesma combinação de `title`, `text` e `source_type`.
* `consolidate` é idempotente por janela de sinais; sem novos sinais, deve produzir no máximo auditoria de noop.
* `request_id` ausente pode ser gerado automaticamente pelo adaptador externo para rastreabilidade.
