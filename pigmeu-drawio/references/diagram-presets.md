# Diagram Presets

Presets are stored in `assets/presets/` as JSON. Use them to keep diagrams consistent.

Core visual defaults now follow the component reference language from `drawop-componentes-examples.drawio` (hand-drawn style, `Architects Daughter`, semantic palette, `hachureAngle=132`, `jiggle=1.7`, and medium sketch strokes).

- `uml.json`: blue/gray, compact technical notation.
- `bpmn.json`: process-oriented, lane-friendly styling.
- `flowchart.json`: simple process colors and decision styling.
- `mindmap.json`: branch color palette and radial spacing.
- `wireframe.json`: grayscale low-fidelity UI components.
- `journey.json`: stage-based journey and service blueprint layouts.

For component-level behavior and semantic color usage, see `references/component-library.md`.

When a preset conflicts with `drawop-componentes-examples.drawio`, prefer the reference file and update the preset instead of drifting to generic draw.io defaults.
