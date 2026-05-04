# /drawio-export

Export an existing `.drawio` file.

```bash
/drawio-export @diagram.drawio --format png --embed
```

## PNG-first examples

```bash
/drawio-export @diagram.drawio --format png --output diagram.png
/drawio-export @diagram.drawio --format png --preview --output diagram.preview.png
/drawio-export @diagram.drawio --format png --embed --scale 2 --output diagram.drawio.png
```

## Recommended validation sequence

```bash
python3 scripts/drawio_validate.py diagram.drawio
python3 scripts/check_layout.py diagram.drawio
bash scripts/drawio_export.sh diagram.drawio --format png --output diagram.png
```

## If embedded PNG looks corrupted

```bash
python3 scripts/repair_png_iend.py diagram.drawio.png
```
