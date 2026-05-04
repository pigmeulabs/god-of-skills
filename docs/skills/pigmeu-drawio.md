# Skill: pigmeu-drawio

## Objetivo

Gerar, editar, validar, previewar e exportar diagramas draw.io usando o vocabulario visual canonico Pigmeu.

## Local canonico

- `pigmeu-drawio/`

## Referencia visual canonica

- `pigmeu-drawio/drawop-componentes-examples.drawio`
- `pigmeu-drawio/references/component-library.md`
- `pigmeu-drawio/references/diagram-presets.md`
- `pigmeu-drawio/assets/presets/*.json`

## Padrao de estilo

- Fonte principal: `Architects Daughter`.
- Fonte secundaria: `Helvetica` apenas para labels curtos de conectores, como `SIM` e `NAO`.
- Blocos: `fontSize=16`, `rounded=1`, `shadow=1`, `sketch=1`, `strokeColor=#36393d`, `strokeWidth=2`.
- Textura: `fillWeight=2`, `hachureGap=3`, `hachureAngle=132`, `jiggle=1.7`.
- Espacamento interno: `spacingLeft=10`, `spacingRight=10`, `spacingTop=5`, `spacingBottom=5`.
- Headers de swimlane: `fontSize=26`, `fontStyle=1`, `fillColor=#cce5ff`.
- BPMN: eventos `fontSize=20`; gateways `shape=mxgraph.bpmn.gateway2`, `fillColor=#FFFF00`.
- Wireframes: campos com labels `fontSize=12`, valores `fontSize=16`, botoes/chips `fontSize=13`.

## Regra operacional

- Ao criar diagramas, copiar o padrao mais proximo da biblioteca de componentes antes de inventar estilos novos.
- Evitar estilo corporativo flat, Arial generico e Helvetica em blocos principais.
- Se um preset divergir de `drawop-componentes-examples.drawio`, atualizar o preset para seguir a referencia.
