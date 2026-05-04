---
name: pigmeu-drawio
description: generate, edit, validate, preview, and export draw.io diagrams for uml, bpmn, flowcharts, mind maps, wireframes, user journeys, process models, system behavior, and product planning. use when the user asks to create a draw.io diagram, model a process, design a flow, create uml diagrams, create bpmn diagrams, build a mind map, draft a wireframe, convert requirements into diagrams, edit .drawio files, validate draw.io xml, or export diagrams to png svg pdf jpg in opencode.
---

# Pigmeu Drawio

## Purpose

Create documentation-ready draw.io diagrams for visual modeling tasks in OpenCode. Focus on UML, BPMN, flowcharts, mind maps, wireframes, user journeys, service blueprints, and process/product planning. Avoid cloud icon catalog workflows; this skill is not an AWS/GCP/Azure/Kubernetes icon lookup skill.

This skill uses `drawop-componentes-examples.drawio` as the canonical component and style reference for visual language.

## Operating workflow

1. Classify the request: create, edit, validate, preview, export, convert, or troubleshoot.
2. Select the diagram type: UML, BPMN, flowchart, mind map, wireframe, user journey, or service blueprint.
3. Produce a short diagram plan before generating XML when the diagram has more than five elements.
4. Generate uncompressed `.drawio` XML as the source of truth.
5. Validate the file with `scripts/drawio_validate.py` before export or delivery.
6. Check layout with `scripts/check_layout.py` for overlap, negative coordinates, small text, and suspicious canvas issues.
7. Export using `scripts/drawio_export.sh` when draw.io Desktop CLI is available.
8. Use `scripts/drawio_url.py` as fallback when CLI or MCP is not available.
9. Repair embedded PNG outputs with `scripts/repair_png_iend.py` after exporting PNG with embedded diagram data.
10. Provide the generated files, export path, and fallback URL if applicable.
11. Record the interaction, diagram summary, and export paths using `pnf-session-memory.record_response` or the `pnf-session-memory-ops` skill.

## Component system

- Default visual language is hand-drawn and must follow `drawop-componentes-examples.drawio`: `fontFamily=Architects Daughter`, `sketch=1`, `fillWeight=2`, `hachureGap=3`, `hachureAngle=132`, `jiggle=1.7`, `strokeColor=#36393d`, `strokeWidth=2`, `rounded=1`, and spacing of `10/10/5/5`.
- Use the observed typography scale: section headers `26` bold, normal process/cards `16`, BPMN events/gateways `20`, pill tags/buttons `13`, field labels `12`, and connector labels may use `Helvetica` only when preserving the reference style for `SIM`/`NAO` labels.
- Use semantic palette consistently:
  - section, info, output, message: `#cce5ff`
  - warning, decision, future scope: `#ffff88` or BPMN gateway `#FFFF00`
  - risk, stop, cancel, mandatory: `#ffcccc`, `#FF0000`, or `#e51400`
  - success, start, approved: `#00FF00` or `#99FF99`
  - neutral, verify, disabled: `#eeeeee`
  - primary UI action or selected item: `#0085FC` or `#007FFF`
- Prefer component families from `drawop-componentes-examples.drawio` and `references/component-library.md`:
  - callouts and tooltips,
  - BPMN events and gateways,
  - arrows and indicators,
  - tasks/cards,
  - notes/tags/markups,
  - wireframe widgets.
- When generating draw.io XML manually, copy the closest style pattern from `references/component-library.md` instead of inventing generic Arial/flat styles.

## Decision tree

- For UML syntax, stereotypes, relationships, lifelines, activities, or states: read `references/uml-rules.md`.
- For process modeling with pools, lanes, events, gateways, and tasks: read `references/bpmn-rules.md`.
- For simple logic or operational flows: read `references/flowchart-rules.md`.
- For concept organization, requirements, or brainstorming: read `references/mindmap-rules.md`.
- For interface layouts, product screens, dashboards, or mobile flows: read `references/wireframe-rules.md`.
- For XML structure, escaping, draw.io cells, and styles: read `references/xml-generation-rules.md`.
- For spacing, typography, routing, and canvas rules: read `references/layout-rules.md`.
- For component selection and semantic styling: read `references/component-library.md`.
- For CLI, MCP, URL fallback, and file formats: read `references/export-rules.md` and `references/mcp-usage.md`.
- For recurring failures: read `references/troubleshooting.md`.

## Mandatory draw.io XML rules

- Use uncompressed XML for source `.drawio` files.
- Always include root cells with `id="0"` and `id="1"`.
- Use unique IDs and stable readable prefixes where practical.
- Use `vertex="1"` for shapes and `edge="1"` for connectors.
- Do not create self-closing edge cells; every edge must include `mxGeometry` with `relative="1"`.
- Escape XML label characters: `&`, `<`, `>`, `"`, and apostrophes when needed.
- Use explicit `fontFamily` on text-bearing cells.
- Prefer coordinates snapped to multiples of 10.
- Keep enough space for labels before exporting.

## Quality bar

A finished diagram must be semantically correct, visually scannable, and editable in diagrams.net. It must avoid overlaps, unreadable labels, disconnected edges, unbalanced layout, and notation misuse. When uncertain, favor fewer elements, clearer grouping, and a short note explaining assumptions.

## Official draw.io MCP usage

Use the official draw.io MCP servers only when available. Do not require MCP for the skill to work.

- Remote MCP: use `mcp/opencode.drawio.remote.json` for `https://mcp.draw.io/mcp` when the client supports remote MCP servers.
- Local MCP: use `mcp/opencode.drawio.local.json` with `npx @drawio/mcp` to open XML, CSV, or Mermaid in the draw.io editor.
- If MCP is unavailable, continue with local XML generation, validation, CLI export, or URL fallback.

## Common commands

```bash
python3 scripts/drawio_validate.py diagram.drawio
python3 scripts/check_layout.py diagram.drawio
bash scripts/drawio_export.sh diagram.drawio --format png --preview --output diagram.preview.png
bash scripts/drawio_export.sh diagram.drawio --format png --embed --scale 2 --output diagram.drawio.png
python3 scripts/repair_png_iend.py diagram.drawio.png
python3 scripts/drawio_url.py diagram.drawio --mode editor
```

## Templates and presets

Use templates in `assets/templates/` as starting points and presets in `assets/presets/` for consistent sizing, fonts, colors, and diagram-specific defaults. Preserve editability; never rasterize source diagrams as the only deliverable.

## PNG export requirement

When the user asks for visual output, export PNG as part of the delivery.

- Mandatory outputs for visual delivery:
  - source `.drawio`
  - exported `.png`
  - reproduction command used
- Preferred export pipeline:
  1. `python3 scripts/drawio_validate.py <file.drawio>`
  2. `python3 scripts/check_layout.py <file.drawio>`
  3. `bash scripts/drawio_export.sh <file.drawio> --format png --output <file.png>`
  4. `python3 scripts/repair_png_iend.py <file.png>` when embedded PNG needs repair
