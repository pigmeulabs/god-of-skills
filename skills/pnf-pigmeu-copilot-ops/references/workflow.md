# Workflow Operacional Minimo

## Objetivo

Construir e manter a base vetorizada do `pigmeu-copilot` com ciclo curto:
bootstrap -> sync -> search/ask -> stats.

## Sequencia recomendada

1. `ensure_bootstrap.py`
2. `run_sync.py`
3. `run_search.py`
4. `run_ask.py`
5. `run_stats.py`

Todos os wrappers seguem estrategia `MCP -> CLI fallback` por default.

## Saidas esperadas

* `run_sync.py`: `indexed_docs >= 1` no primeiro ciclo, `failed_docs = 0`.
* `run_search.py`: hits contendo `doc_id`, `chunk_id`, `path`.
* `run_ask.py`: `answer_short` nao vazio e `sources` com ao menos 1 item.
* `run_stats.py`: contagens coerentes de documentos/chunks/facts.

## Diagnostico rapido

* Se `failed_docs > 0`, revisar arquivos problemáticos e rodar sync novamente.
* Se hits vazios em busca, validar se `sync` indexou docs esperados.
* Se resposta sem fontes, aumentar `--top-k` e verificar base ativa com `run_stats.py`.
