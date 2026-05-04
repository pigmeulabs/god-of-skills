# Troubleshooting

## Skill generated invalid XML

Run:

```bash
python3 scripts/drawio_validate.py diagram.drawio --strict
```

Common causes:

- Missing root cells `0` and `1`.
- Unescaped `&` in labels.
- Edge cell missing `mxGeometry`.
- Duplicate IDs.

## Export fails

Check whether draw.io CLI is installed:

```bash
draw.io --version || drawio --version
```

If unavailable, generate a fallback URL:

```bash
python3 scripts/drawio_url.py diagram.drawio --mode editor
```

## PNG cannot be opened

If exported with embedded diagram data, run:

```bash
python3 scripts/repair_png_iend.py diagram.drawio.png
```

## Diagram is too dense

Split into multiple diagrams:

- Overview.
- Main process.
- Exception path.
- Screen-level wireframe.
- Data/behavior model.
