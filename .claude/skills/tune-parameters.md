# Tune Image Processing Parameters

Interactive OpenCV slider interface for real-time edge detection tuning.

## Usage
```bash
python scripts/tune.py <image_path> -o <output.gcode>
```

## Controls
- Drag sliders to adjust: downscale, CLAHE, XDoG params, morphology, blob filtering
- Press `s` — save parameters to machine.yaml AND generate G-Code
- Press `q` — quit without saving

## Display
- Left panel: original grayscale image
- Right panel: processed edge detection result (inverted for readability)

## Notes
- Saved parameters overwrite `config/machine.yaml`
- After saving, run `scripts/simulate.py` on the output to preview the drawing
