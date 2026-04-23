# MCP Local (pnf-mcp)

Servidor MCP local em Python, adaptador fino sobre `WorkspaceService`.

## Como executar

```bash
PYTHONPATH=src python3 -m pigmeu_never_forget.cli mcp-serve
```

Ou pelo script de entrada:

```bash
pnf-mcp
```

Servidor de memoria de sessoes:

```bash
PYTHONPATH=src python3 -m pigmeu_never_forget.session_memory.server --config /home/ubuntu/projects-workspace/.opencode/pnf-workspace-config.yaml
```

Ou pelo script de entrada:

```bash
pnf-session-mcp
```

## Configuração no OpenCode

No workspace, registrar o MCP em `.opencode/opencode.json` apontando para:

* `/home/ubuntu/projects-workspace/.opencode/scripts/pnf-mcp.sh`
* `/home/ubuntu/projects-workspace/.opencode/scripts/pnf-session-mcp.sh`

Esses wrappers instalados devem permanecer alinhados com os arquivos canônicos:

* `/home/ubuntu/projects-workspace/god-of-skills/opencode/scripts/pnf-mcp.sh`
* `/home/ubuntu/projects-workspace/god-of-skills/opencode/scripts/pnf-session-mcp.sh`

Esse script define `PYTHONPATH` do repositório e executa:

```bash
python3 -m pigmeu_never_forget.mcp --config /home/ubuntu/projects-workspace/.opencode/pnf-workspace-config.yaml
```

Com `PNF_REPO_PATH=/home/ubuntu/projects-workspace/god-of-skills/projects/pigmeu-never-forget`.

Chamadas locais sem transporte (útil para fallback em wrappers):

```bash
PYTHONPATH=src python3 -m pigmeu_never_forget.mcp.local_call search_project --payload '{"project_id":"pigmeu-copilot","query":"auth"}'
PYTHONPATH=src python3 -m pigmeu_never_forget.session_memory.local_call latest_session
PYTHONPATH=src python3 -m pigmeu_never_forget.session_memory.local_call record_response --payload '{"prompt":"...","response":"...","model":"gpt-5"}'
```

Dependencia opcional:

```bash
pip install ".[mcp]"
```

## Tools disponiveis (v1)

* `list_projects()`
* `sync_project(project_id, mode='incremental', force=false)`
* `index_text(project_id, title, text, source_type='inline_text', tags=[])`
* `search_project(project_id, query, top_k=8, expand=false)`
* `ask_project(project_id, question, top_k=6, allow_summary_only=true)`
* `get_project_stats(project_id)`
* `consolidate_project(project_id, mode='incremental')`
* `get_job_status(project_id, job_id)`

## Tools disponiveis (session memory)

* `start_session(payload?)`
* `append_turn(payload?)`
* `record_response(payload?)`
* `update_metrics(payload?)`
* `finalize_session(payload?)`
* `archive_session(payload?)`
* `rollover_stale_sessions(payload?)`
* `get_session_status(payload?)`
* `latest_session(request_id?)`

## Resources disponiveis (v1)

* `rag://projects`
* `rag://project/{project_id}/summary`
* `rag://project/{project_id}/stats`
* `rag://project/{project_id}/jobs/{job_id}`

## Envelope de resposta

Sucesso:

```json
{
  "status": "ok",
  "data": {},
  "meta": {
    "project_id": "pigmeu-copilot"
  }
}
```

Erro:

```json
{
  "status": "error",
  "error": {
    "code": "PROJECT_NOT_FOUND",
    "message": "Project not found",
    "retryable": false,
    "details": {}
  }
}
```

## Notas operacionais

* Modo local-first/single-node.
* Sem scheduler no v1.
* Locking e concorrencia herdados dos servicos centrais.
* `request_id` opcional em tools para correlacao; se ausente, o servidor gera automaticamente.
* Eventos MCP sao persistidos em `state.db.log_events` com `service='mcp'` e `trace_id=request_id`.
