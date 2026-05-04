# Component Library

Use this library with `drawop-componentes-examples.drawio` as the reference catalog. The file has three reference pages: `componentes`, `exemplo-fluxograma-1`, and `exemplo-wireframe-1`.

## Global style tokens

- Font: `Architects Daughter`
- Base text size: `16`
- Header text size: `26`, bold
- BPMN event/gateway text size: `20`
- Pill tag and button text size: `13`
- Field label text size: `12`
- Stroke color: `#36393d`
- Typical stroke width: 2
- Sketch settings: `sketch=1`, `fillWeight=2`, `hachureGap=3`, `hachureAngle=132`, `jiggle=1.7`
- Base geometry style: `rounded=1`, `arcSize=6`, `spacingLeft=10`, `spacingRight=10`, `spacingTop=5`, `spacingBottom=5`
- Use `shadow=1` for swimlanes, process cards, broad arrows, notes, and action blocks. Use `shadow=0` for compact BPMN events/gateways and connector-like indicators.
- Preserve `fontSource=https%3A%2F%2Ffonts.googleapis.com%2Fcss%3Ffamily%3DArchitects%2BDaughter` when generating full draw.io style strings.

Canonical base block style:

```text
rounded=1;whiteSpace=wrap;html=1;fontFamily=Architects Daughter;fontSize=16;fontColor=default;fillColor=#eeeeee;strokeColor=#36393d;strokeWidth=2;sketch=1;fillWeight=2;hachureGap=3;hachureAngle=132;jiggle=1.7;disableMultiStroke=0;disableMultiStrokeFill=1;fillStyle=solid;curveFitting=0;align=center;verticalAlign=middle;spacingLeft=10;spacingRight=10;spacingTop=5;spacingBottom=5;arcSize=6;shadow=1;
```

## Semantic palette

- `#cce5ff`: info, output, container headers
- `#ffff88`: warning, important note, future scope
- `#FFFF00`: BPMN gateway and high-visibility decision
- `#ffcccc`: soft risk, blocked path, safe stop
- `#FF0000`: hard cancel, destructive action, terminal risk
- `#e51400`: mandatory tag or high-contrast danger label
- `#00FF00`: positive status, start, success
- `#99FF99`: approved task or successful process action
- `#eeeeee`: neutral, verify, disabled
- `#FFFFFF`: chips, file paths, script/agent labels, modal cards
- `#0085FC`: primary UI action
- `#007FFF`: selected menu item

## Components by family

### Callouts and tooltips

- Shapes: `mxgraph.basic.rectCallout`, `mxgraph.basic.roundRectCallout`
- Use for explanatory notes linked to a nearby element.
- Avoid replacing BPMN/flowchart semantics with callouts.
- Rectangular callouts use `dx=40.33`, `dy=23`, `boundedLbl=1`, `shadow=0`, size around `180x110`, and fills `#eeeeee`, `#ffff88`, or `#ffcccc`.
- Rounded callouts use `mxgraph.basic.roundRectCallout`, `dx=36.38`, `dy=21`, `size=12.76`, `shadow=1`, and the same semantic fills.

### BPMN events and gateways

- Shapes: `mxgraph.bpmn.event`, `mxgraph.bpmn.gateway2`
- Use for process behavior, branching, signaling, and lifecycle events.
- Keep labels short and semantic.
- Events are usually `50x50`, `aspect=fixed`, `perimeter=ellipsePerimeter`, `fontSize=20`, `shadow=0`, `hachureGap=4`, `curveFitting=1`.
- Start/success events use green fills such as `#00FF00` with stroke `#00CC00` or `#006633`; terminal/cancel events use red strokes/fills; message events use `#cce5ff` with `#36393d`.
- Gateways are usually `55x55` or `60x60`, `fillColor=#FFFF00`, `strokeColor=#1A1A1A`, `strokeWidth=2`, `fontSize=20`, `aspect=fixed`, and `perimeter=rhombusPerimeter`.

### Arrows and indicators

- Shapes: `mxgraph.arrows2.*` for visual indicators.
- Edge styles: mix `classic`, `open`, dashed, and start markers only when semantically needed.
- Prefer normal connectors for primary process flow.
- Broad task arrows use `mxgraph.arrows2.arrow`, `shadow=1`, sizes around `260x120` or `280x110`, and fills `#b1ddf0`, `#ffff88`, or `#eeeeee`.
- Primary flow connectors use `edgeStyle=orthogonalEdgeStyle`, `rounded=0`, `sketch=1`, `curveFitting=1`, `jiggle=1` or `2`, `strokeWidth=2`, `endArrow=classic`.
- Connector labels may use `Helvetica` at `fontSize=22` for `SIM`/`NAO` when matching the reference flowchart.

### Tasks and cards

- Shape: rounded rectangles with sketch style.
- Use verb + object labels for process tasks.
- Keep one action per block.
- Typical task/card size is `260x120`.
- Use `#eeeeee` for neutral steps, `#ffff88` for sanitize/backup/caution steps, `#99FF99` for AI/validated/generated success steps, and `#E5CCFF` for external API callouts when needed.

### Notes, tags, markups

- Shapes: note/post-it style and pill tags.
- Examples: `MANDATORIO`, `IMPORTANTE`, `INPUT`, `OUTPUT`, `ESCOPO FUTURO`, `VERIFICAR`.
- Use to annotate, not to encode main flow logic.
- Notes use `shape=note`, `fontSize=16`, `line-height: 140%`, and fills `#F8FF33`, `#cce5ff`, or `#e51400`.
- Pill tags use rounded rectangles with `arcSize=21`, `fontSize=13`, `fontStyle=1`, and white font on strong danger/primary fills when needed.
- Path/script/agent chips use `fillColor=#FFFFFF`, `strokeColor=#36393d`, `fontSize=14`, `align=left`, and extra left spacing for optional icons.

### Wireframe widgets

- Inputs, dropdowns, date pickers, pagination, modal actions, status blocks.
- Use low/medium fidelity only; structure and hierarchy over decoration.
- Keep labels concrete and aligned to the requested screen behavior.
- Field labels use `fontSize=12`; field values use `fontSize=16`.
- Page/header titles use `fontSize=28`; menu titles use `fontSize=20`; menu items use `fontSize=18`.
- Primary buttons use `fillColor=#0085FC`; destructive buttons use `#FF0000`; secondary/disabled buttons use `#eeeeee` or `#FFFFFF`.
- Selected pagination/menu items use blue fills like `#3399FF` or `#007FFF`.
- Disabled UI states use `fillColor=#eeeeee` and `strokeColor=#B3B3B3` or `#666666`.

## Selection rules by diagram type

- `bpmn`: prioritize BPMN events/gateways/tasks; tags and notes as secondary.
- `flowchart`: prioritize process/decision/connectors; callouts for clarifications.
- `wireframe`: prioritize UI widgets, cards, buttons, and state labels.
- `uml`: prioritize UML notation; use this library only for emphasis notes/tags.
- `mindmap`: prioritize branch readability; use tags sparingly.

## Avoid

- Mixing too many accent colors in the same local area.
- Using decorative arrows where semantic connectors are expected.
- Replacing notation symbols with generic boxes.
- Falling back to Arial/system font when this style is requested.
- Using flat, perfectly clean corporate styling when the reference visual language is expected.
- Overusing `Helvetica`; reserve it for connector decision labels when copying the example pattern.
