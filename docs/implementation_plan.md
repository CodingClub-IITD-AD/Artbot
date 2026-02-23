# ArtBot: Image → G-Code Pipeline + Simulator

Build two working scripts: (1) convert an image to plotter G-Code, (2) visually simulate the G-Code output with an animated pen.

## Proposed Changes

### Config

#### [NEW] `config/machine.yaml`
All machine constants in one place: frame size (1800×1200mm), 50mm buffer, work area (1700×1100mm), feed rates, pen servo commands, and image processing defaults.

---

### `artbot/` Python Package

#### [NEW] `artbot/image_processing/preprocess.py`
- `load_image(path)` → grayscale numpy array
- `detect_edges(img, mode)` → binary image via Canny (photos) or threshold (sketches)

#### [NEW] `artbot/image_processing/trace.py`
- `extract_contours(binary)` → list of point arrays
- `simplify_contours(contours, epsilon)` → Douglas-Peucker simplified paths

#### [NEW] `artbot/gcode_generation/generator.py`
- `generate_gcode(paths, config)` → G-Code string with `G0`/`G1` moves, `M3 S90`/`M5` pen commands, header/footer

#### [NEW] `artbot/gcode_generation/path_sorting.py`
- Nearest-neighbor sort to minimize pen-up travel distance

#### [NEW] `artbot/gcode_generation/clipping.py`
- Clip/scale all paths to fit within the 1700×1100mm safe zone

#### [NEW] `artbot/utils/config_loader.py`
- Load and validate `machine.yaml`

---

### CLI Scripts

#### [NEW] `scripts/convert.py`
```
python scripts/convert.py input.jpg -o output.gcode --mode auto
```
Modes: `auto` (detect if sketch or photo), `sketch`, `photo`. Reads config from `config/machine.yaml`.

#### [NEW] `scripts/simulate.py`
```
python scripts/simulate.py output.gcode
```
Matplotlib animation showing:
- Whiteboard frame (gray) + safe zone (dashed)
- Pen-down lines drawn in blue, progressively
- Pen-up travel in faint gray dashed lines
- Red dot for current pen position
- Stats overlay: progress %, total distance, estimated time

---

### Project Files

#### [NEW] `requirements.txt`
`opencv-python`, `numpy`, `matplotlib`, `pyyaml`

#### [NEW] `.gitignore`
Standard Python gitignore + `output/` directory

---

## Verification Plan

### Automated (end-to-end test)
1. Generate a test image (black rectangle on white) programmatically
2. Run `python scripts/convert.py test_rect.png -o test.gcode`
3. Verify the `.gcode` file contains valid G-Code (G0/G1/M3/M5 commands, coordinates within bounds)
4. Run `python scripts/simulate.py test.gcode --no-animate` (static plot mode) to confirm it renders without error

### Visual (manual)
1. Run converter on a real sketch image
2. Run simulator in animation mode — confirm the pen traces the expected outline
