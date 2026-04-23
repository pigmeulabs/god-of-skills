# ADR 003: Consolidação AutoDream-like

## Status

Aceita

## Contexto

O sistema precisa manter memória útil por projeto sem depender do histórico de sessão e sem reprocessar o workspace inteiro.

## Decisão

Executar consolidação incremental por projeto com quatro operações:

* `prune`: desativar fatos obsoletos ou redundantes
* `merge`: unir aliases e fatos equivalentes
* `refresh`: reescrever resumos e fatos válidos quando houver novo contexto
* `rebuild`: atualizar índices derivados compactos

## Guardrails

* Nunca alterar arquivos-fonte.
* Toda alteração gera auditoria com antes/depois quando houver mutação material.
* Conflito entre fatos mantém o anterior como ativo até substituição explícita com evidência e confiança maior.

## Consequências

* A memória fica mais compacta e útil para prompt.
* O sistema precisa de critérios explícitos de confiança, evidência e rollback lógico.
