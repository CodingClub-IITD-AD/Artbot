# ArtBot - Vertical Whiteboard Plotter

## Project Overview
ArtBot is a large-scale robotic drawing machine that converts digital images into pen drawings on a vertical whiteboard (180x120cm). The system uses a 3-axis Cartesian motion system fighting gravity, controlled by Arduino + GRBL firmware, with a Python-based image-to-G-Code pipeline.

## Key Specs
- **Board**: 180cm x 120cm, mounted vertically (perpendicular to ground)
- **Buffer**: 5cm on all sides → usable drawing area: **170cm x 110cm**
- **Origin**: top-left corner
- **Motion**: Dual-Y Cartesian, belt-driven (no counterweights — motors have enough torque)
- **Motors**: 2x NEMA 23 steppers (Y-axis) + 1x NEMA 23 stepper (X-axis) + 1x SG90 servo (pen Z)
- **Controller**: Arduino Uno + CNC Shield V3 + TMC2209 drivers
- **Firmware**: GRBL (G-Code interpreter, real-time motor control)
- **Resolution**: 80 steps/mm (200 steps x 16 microsteps / 20-tooth x 2mm GT2 belt)

## Mechanical Architecture
- **Y-axis**: Two vertical rails (left/right), dual synchronized motors at top corners
- **X-axis**: Single 180cm horizontal rail moves up/down on Y rails; pen carriage rides along it
- **Z-axis**: Spring-loaded pen holder with SG90 servo (spring pushes pen toward board, servo retracts)
- **No counterweights**: NEMA 23 motors provide sufficient torque to drive the Y-axis against gravity directly
- **Critical**: Dual-Y motors face opposite directions — one motor's coil wiring MUST be reversed

## Software Pipeline
```
Image → Preprocess → Edge Detect (XDoG) → Contour Extract → Scale/Clip → Path Sort → G-Code
```

### Project Structure
```
artbot/
  image_processing/
    preprocess.py    # load_image, detect_edges (sketch/photo/auto via XDoG)
    trace.py         # extract_contours, simplify_contours (Douglas-Peucker)
  gcode_generation/
    generator.py     # generate_gcode (G0/G1/M3/M5 output)
    clipping.py      # scale_and_clip (pixel→mm, center in work area)
    path_sorting.py  # sort_paths_nearest (greedy nearest-neighbor)
  utils/
    config_loader.py # load_config (YAML reader)
config/
  machine.yaml       # all machine constants + processing params
scripts/
  convert.py         # CLI: image → .gcode
  simulate.py        # CLI: .gcode → matplotlib animation
  tune.py            # CLI: interactive OpenCV slider tuner
```

### Key G-Code Commands
- `G0` — rapid travel (pen up), `G1` — draw move (pen down)
- `M3 S90` — pen down, `M5` — pen up
- `G4 Pn` — dwell (pen settle time)
- `M2` — program end

## Tech Stack
- **Language**: Python 3.13+
- **Dependencies**: opencv-python, numpy, matplotlib, pyyaml
- **Environment**: Use the `gpy` global venv (do NOT create project-local venvs unless asked)

## Development Guidelines
- All coordinates are in millimeters
- G-Code Y increases downward (origin = top-left, matches image coordinates)
- Paths are Nx2 numpy arrays of [x, y] points
- Config lives in `config/machine.yaml` — the tuner script can overwrite it
- When modifying image processing, test with `scripts/tune.py` for visual feedback
- When modifying G-Code generation, verify with `scripts/simulate.py`
- Keep processing parameters tunable via machine.yaml, not hardcoded

## Hardware Context (for software decisions)
- Board is VERTICAL — gravity pulls pen away from surface (spring compensates)
- NEMA 23 motors drive Y-axis directly against gravity (no counterweights)
- 80 steps/mm resolution means pen tip width (0.5-1.0mm) >> step size (0.0125mm)
- GRBL look-ahead smooths segmented curves at the firmware level
- Long 180cm X-rail can vibrate — software should avoid extremely rapid direction changes

## Team
- 6-person team, new to robotics
- Currently in design/procurement phase for hardware
- Software pipeline (this repo) is functional for image→G-Code→simulation
- Next milestone: present docs to robotics club for hardware feedback
