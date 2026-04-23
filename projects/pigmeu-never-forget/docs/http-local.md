# HTTP Local (FastAPI)

Adapter HTTP fino sobre o núcleo (`WorkspaceService`), alinhado com `docs/api-contracts.md`.

## Como executar

```bash
PYTHONPATH=src python3 -m pigmeu_never_forget.cli api-serve --host 127.0.0.1 --port 8787
```

Ou via entrypoint:

```bash
pnf-api
```

Dependências:

```bash
pip install ".[api]"
```

## Endpoints principais

* `GET /health`
* `GET /projects`
* `POST /projects/discover`
* `POST /projects/{project_id}/sync`
* `POST /projects/{project_id}/index-text`
* `POST /projects/{project_id}/search`
* `POST /projects/{project_id}/ask`
* `POST /projects/{project_id}/consolidate`
* `GET /projects/{project_id}/stats`
* `GET /projects/{project_id}/jobs/{job_id}`

## Headers

* `X-Request-Id` opcional

Quando ausente, o servidor gera automaticamente e devolve em `meta.request_id`.

## Envelope

Sucesso:

```json
{
  "status": "ok",
  "data": {},
  "meta": {
    "project_id": "project-a",
    "request_id": "req_123"
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
  },
  "meta": {
    "request_id": "req_123"
  }
}
```

