# Fonte da Verdade

## Regra principal

`god-of-skills` e o repositório canônico para:

- evolucao do `pigmeu-never-forget`
- criacao e manutencao de skills
- criacao e manutencao de MCPs locais
- scripts de integracao com OpenCode
- documentacao operacional e arquitetural

## Relacao com `.opencode/`

O diretório `.opencode/` nao e a fonte da verdade. Ele existe como instalacao local de runtime.

- `skills/` em `.opencode/` sao espelhos instalados
- `scripts/` em `.opencode/` sao wrappers usados pelo OpenCode
- `opencode.json` referencia os artefatos canonicos hospedados no monorepo

## Relacao com repositorios de projeto

O codigo-fonte do `pigmeu-never-forget` agora e mantido em:

- `projects/pigmeu-never-forget/`

Se houver copias antigas fora do monorepo, elas devem ser tratadas como legadas ou espelhos temporarios.

## Fluxo recomendado

1. Implementar no monorepo.
2. Executar testes no projeto canonico.
3. Atualizar docs centrais e docs do projeto.
4. Sincronizar runtime OpenCode.
5. Validar MCPs conectados.
