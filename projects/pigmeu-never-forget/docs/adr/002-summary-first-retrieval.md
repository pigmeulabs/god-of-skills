# ADR 002: Summary-first retrieval

## Status

Aceita

## Contexto

O sistema é otimizado para orçamento baixo de contexto e uso por agentes.

## Decisão

A ordem padrão de recuperação é:

1. `active_facts`
2. `project_summary_short`
3. summaries documentais relevantes
4. busca vetorial
5. expansão para chunks completos apenas se necessário

## Consequências

* Reduz custo por consulta.
* Exige manutenção disciplinada de summaries e fatos ativos.
* Pode perder nuance se summaries estiverem degradados; por isso auditoria e refresh são obrigatórios.
