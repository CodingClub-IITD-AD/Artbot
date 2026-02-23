# ArtBot: Image → G-Code + Simulator

## Pipeline Scripts
- [x] Set up repo structure (`config/`, `artbot/`, `scripts/`, `requirements.txt`)
- [x] Machine config (`config/machine.yaml`)
- [x] Image preprocessing module (grayscale, edge detection, thresholding)
- [x] Contour tracing module (extract + simplify contours)
- [x] G-Code generation (path sorting, boundary clipping, gcode output)
- [x] CLI converter script (`scripts/convert.py`)
- [x] G-Code simulation/visualizer (`scripts/simulate.py`)
- [x] Test end-to-end with a sample image
