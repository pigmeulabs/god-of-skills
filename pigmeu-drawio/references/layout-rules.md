# Layout Rules

## Global spacing

- Snap coordinates to multiples of 10.
- Keep at least 30 px between unrelated shapes.
- Keep at least 20 px between arrowheads and nearby labels.
- Prefer left-to-right for system interactions and top-to-bottom for processes.
- Keep the happy path straight; put exceptions on side branches.

## Typography

- Use 14 px minimum for body labels.
- Use 16-18 px for titles and primary nodes.
- Use explicit `fontFamily` on all text-bearing cells.
- Avoid long sentences in nodes; use verb + object for tasks.

## Containers

- Use containers for packages, lanes, screens, modules, or grouped branches.
- Keep at least 30 px internal margin.
- Use low-contrast fill colors for containers.
- Do not connect edges to container borders unless the container itself is the semantic target.

## Routing

- Reserve vertical or horizontal corridors for multiple connectors.
- Avoid crossing shapes.
- Use waypoints for complex edges.
- Spread incoming/outgoing connectors with `entryX`, `entryY`, `exitX`, and `exitY` when several edges touch the same shape.
