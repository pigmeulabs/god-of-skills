# Ciclo de Vida de Jobs

Este documento fecha a política operacional de execução, concorrência e recuperação.

## Tipos de job

* `discover`
* `sync`
* `index`
* `query`
* `consolidate`

## Estados

```text
queued -> running -> succeeded
queued -> running -> failed
queued -> running -> cancelled
```

Regras:

* `heartbeat_at` deve ser atualizado periodicamente enquanto o job estiver em `running`.
* Job sem heartbeat por mais de 2x o intervalo configurado é elegível para recuperação.

## Locks por projeto

* `sync` e `consolidate` exigem lock exclusivo por projeto.
* `query` não exige lock, mas deve observar snapshot consistente do estado persistido.
* `sync` e `consolidate` nunca rodam em paralelo no mesmo projeto.
* `discover` é global e não pode iniciar `sync` duplicado para o mesmo projeto.

## Política de concorrência

* `ask` durante `sync`: permitido. Consulta usa o último estado consistente confirmado.
* `ask` durante `consolidate`: permitido. Consulta usa `project_summary` e `memory_facts` anteriores até o commit final da consolidação.
* `sync` durante `consolidate`: bloqueado com `PROJECT_LOCKED`.
* `consolidate` durante `sync`: bloqueado ou enfileirado, conforme trigger.

## Política de retries

* Timeout, 429 e 5xx de provedores são `retryable`.
* Erros de validação, schema e parsing malformado não são `retryable` sem mudança de entrada.
* Retry exponencial com jitter.
* Rotação de chave ocorre antes de novo retry para falhas elegíveis em provedores.

## Recuperação pós-crash

1. No boot do serviço, localizar jobs `running` com heartbeat expirado.
2. Marcar como `failed` com motivo `stale_heartbeat`.
3. Reconciliar estado:
   * validar locks expirados
   * comparar `chunks` locais com `qdrant_point_id`
   * reenfileirar unidades pendentes
4. Liberar lock órfão.

## Reentrada segura

* `sync` pode ser reexecutado sem limpar estado prévio.
* `consolidate` não reescreve fatos ativos sem registrar `before_json` e `after_json`.
* Upserts vetoriais devem ser determinísticos por `chunk_id`.

## Cenários operacionais obrigatórios

### Indexação inicial

* Cria `.rag/`, banco, coleção e checkpoints.

### Incremental sem mudança

* Não gera embeddings nem atualiza summaries.

### Rename sem mudança de conteúdo

* Marca o documento antigo como removido lógico e cria referência nova reaproveitando hashes compatíveis.

### Exclusão

* Remove do índice vetorial e marca estado relacional como `deleted`.

### Falha no meio do job

* O próximo `sync` reconcilia sem duplicar chunks ativos.
