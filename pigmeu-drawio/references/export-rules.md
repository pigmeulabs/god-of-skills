# Export Rules

## Preferred deliverables

Always keep the `.drawio` source. Export images or documents as secondary artifacts.

When visual delivery is requested, PNG export is mandatory.

- Editable source: `diagram.drawio`
- Preview image: `diagram.preview.png`
- Editable PNG: `diagram.drawio.png`
- Editable SVG: `diagram.svg`
- Document export: `diagram.pdf`

## CLI workflow

Use draw.io Desktop CLI when installed:

```bash
python3 scripts/drawio_validate.py diagram.drawio
python3 scripts/check_layout.py diagram.drawio
bash scripts/drawio_export.sh diagram.drawio --format png --preview --output diagram.preview.png
bash scripts/drawio_export.sh diagram.drawio --format png --embed --scale 2 --output diagram.drawio.png
bash scripts/drawio_export.sh diagram.drawio --format svg --embed --output diagram.svg
bash scripts/drawio_export.sh diagram.drawio --format pdf --embed --output diagram.pdf
```

After embedded PNG export, run:

```bash
python3 scripts/repair_png_iend.py diagram.drawio.png
```

If you only need one final PNG artifact:

```bash
bash scripts/drawio_export.sh diagram.drawio --format png --output diagram.png
```

## Fallback URL

If the CLI is unavailable, generate an editor URL:

```bash
python3 scripts/drawio_url.py diagram.drawio --mode editor
```

In fallback mode, still deliver the `.drawio` source and the command required to export PNG once CLI becomes available.

## Linux headless

If there is no display, use `xvfb-run` automatically through `drawio_export.sh` when installed. If export fails as root or in sandboxed environments, retry with `--disable-gpu --no-sandbox`.
