# XML Generation Rules

Use uncompressed draw.io XML as the source format. Prefer full `<mxfile><diagram><mxGraphModel><root>...</root></mxGraphModel></diagram></mxfile>` files over fragments.

## Required structure

- Include `mxCell id="0"` as the root cell.
- Include `mxCell id="1" parent="0"` as the default layer.
- Shapes are `mxCell` elements with `vertex="1"` and `parent="1"` or a container parent.
- Connectors are `mxCell` elements with `edge="1"`, `source`, `target`, and a child `mxGeometry relative="1" as="geometry"`.
- Keep IDs unique. Use prefixes like `actor-1`, `usecase-1`, `edge-1`, `lane-1`, `wire-btn-1`.

## Labels and escaping

- Escape `&` as `&amp;`.
- Escape `<` as `&lt;` and `>` as `&gt;`.
- Keep labels short; use notes or annotations for longer explanations.
- Use line breaks with `&lt;br&gt;` only when necessary.

## Styles

- Styles are semicolon-delimited `key=value;` pairs.
- Include explicit `fontFamily=Arial` or another selected font on text-bearing cells.
- Use `rounded=1;whiteSpace=wrap;html=1;` for most text shapes.
- Use consistent `strokeColor`, `fillColor`, and `fontColor` from a preset.

## Connectors

- Do not self-close edge cells.
- Prefer orthogonal connectors for structured diagrams: `edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;`.
- Label decision branches clearly, for example `sim`, `não`, `approved`, `rejected`.
