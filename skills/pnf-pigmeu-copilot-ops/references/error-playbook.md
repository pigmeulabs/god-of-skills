# Error Playbook

## PROJECT_NOT_FOUND

**Sintoma**: projeto nao encontrado durante `sync/search/ask/stats`.  
**Acao**:
1. Validar `PNF_PROJECT_PATH` e `PNF_PROJECT_ID`.
2. Rodar `python3 scripts/ensure_bootstrap.py`.
3. Reexecutar comando original.

## PROJECT_LOCKED

**Sintoma**: lock ativo por job concorrente.  
**Acao**:
1. Aguardar conclusao do job em andamento.
2. Reexecutar o comando.
3. Se lock persistir, checar estado de jobs no `state.db`.

## VECTOR_STORE_ERROR

**Sintoma**: erro de persistencia/busca vetorial.  
**Acao**:
1. Rodar `run_sync.py` novamente para reconciliação.
2. Validar backend configurado (`local` ou `qdrant`) no `project.yaml`.
3. Se backend for Qdrant, validar disponibilidade do endpoint.

## INTERNAL_ERROR

**Sintoma**: erro nao mapeado.  
**Acao**:
1. Capturar payload completo retornado pelos scripts.
2. Verificar stack/trace local no comando executado.
3. Repetir com `run_stats.py` para validar estado geral da base.

