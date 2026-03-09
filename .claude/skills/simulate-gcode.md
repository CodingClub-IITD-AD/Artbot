# Simulate G-Code

Visualize generated G-Code as an animated or static pen plotter preview.

## Usage
```bash
# Animated (default)
python scripts/simulate.py <file.gcode> --speed 5

# Static preview
python scripts/simulate.py <file.gcode> --no-animate
```

## Options
- `--speed <int>` — segments per animation frame (default: 5)
- `--no-animate` — show final static result
- `--config <path>` — custom machine.yaml

## What It Shows
- Gray frame boundary (180x120cm)
- Green dashed safe zone (170x110cm)
- Dark lines for pen-down drawing
- Faint dotted lines for pen-up travel
- Red dot for current pen position (animated mode)
- Stats: draw distance, travel distance, estimated time, segment count
