# Convert Image to G-Code

Run the full image-to-gcode conversion pipeline.

## Usage
```bash
python scripts/convert.py <image_path> -o <output.gcode> --mode auto
```

## Options
- `--mode auto|sketch|photo` — processing mode (default: auto)
- `--feed-rate <int>` — override draw feed rate in mm/min
- `--epsilon <float>` — path simplification tolerance in mm
- `--config <path>` — custom machine.yaml path

## Pipeline Steps
1. Load image → grayscale
2. Edge detection (XDoG for photos, threshold for sketches)
3. Contour extraction and filtering
4. Scale to work area (170x110cm) + center + clip
5. Douglas-Peucker simplification
6. Nearest-neighbor path sorting
7. G-Code generation with pen up/down commands
