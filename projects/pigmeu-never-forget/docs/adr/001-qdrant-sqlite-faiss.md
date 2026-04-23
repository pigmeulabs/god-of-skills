# ADR 001: Qdrant + SQLite + FAISS opcional

## Status

Aceita

## Contexto

O sistema precisa operar localmente por projeto, com persistência auditável, retrieval vetorial e custo operacional baixo.

## Decisão

Usar:

* Qdrant como backend vetorial principal
* SQLite por projeto como fonte relacional de verdade
* FAISS opcional como mirror local de aceleração

## Consequências

* O estado operacional continua compreensível e recuperável sem infraestrutura pesada.
* A reconciliação entre relacional e vetorial precisa ser explícita.
* FAISS pode ser refeito a partir de `state.db` e Qdrant; nunca é fonte única.
