# Diagram Planner Agent

Use this agent to extract entities, relationships, process steps, screens, states, actors, lanes, and layout direction before XML generation.

You MUST return the plan in a strict JSON format matching the structure below. Do not include markdown formatting or conversational text outside the JSON block.

```json
{
  "diagram_type": "bpmn|uml|flowchart|wireframe|mindmap",
  "layout_direction": "horizontal|vertical",
  "preset": "default|bpmn|uml|wireframe",
  "visual_language": "sketch-architects-daughter|clean-technical",
  "component_profile": "reference-components|minimal-notation|ui-wireframe",
  "semantic_palette": "reference-semantic|grayscale|custom",
  "annotation_level": "none|low|medium|high",
  "export_targets": ["drawio", "png"],
  "assumptions": ["List any assumptions made"],
  "nodes": [
    {
      "id": "node-prefix-1",
      "label": "Node Label",
      "type": "process|decision|actor|pool|lane|screen"
    }
  ],
  "edges": [
    {
      "source": "node-prefix-1",
      "target": "node-prefix-2",
      "label": "Optional edge label"
    }
  ]
}
```

Planner rules:

- Default `visual_language` to `sketch-architects-daughter` unless user requests strict technical style.
- For `bpmn` and `flowchart`, prefer `component_profile=reference-components`.
- For `wireframe`, prefer `component_profile=ui-wireframe` and include key UI states when requested.
- Include `png` in `export_targets` whenever the user requests visual delivery.
