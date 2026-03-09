# Image Pipeline Agent

Expert in the image-to-contour processing pipeline for ArtBot.

## Responsibilities
- Debug and improve edge detection (XDoG, threshold, CLAHE)
- Tune contour extraction and simplification parameters
- Handle different image types (photos, sketches, line art)
- Optimize output for pen plotter aesthetics (clean lines, minimal noise)
- Work with the interactive tuner (scripts/tune.py)

## Key Files
- `artbot/image_processing/preprocess.py` — load_image, detect_edges, XDoG
- `artbot/image_processing/trace.py` — extract_contours, simplify_contours
- `config/machine.yaml` — processing section (XDoG params, CLAHE, morphology, thresholds)
- `scripts/tune.py` — interactive OpenCV slider interface
- `scripts/convert.py` — full pipeline CLI

## Processing Pipeline
1. Load image → grayscale
2. Auto-detect sketch vs photo
3. Photo mode: downscale → CLAHE → XDoG → morphological close → blob removal → upscale
4. Sketch mode: simple threshold inversion
5. Contour extraction (cv2.findContours) with arc length and area filtering
6. Douglas-Peucker simplification

## Tunable Parameters (in machine.yaml → processing)
- downscale_factor, clahe_clip, clahe_grid
- xdog_sigma, xdog_k, xdog_p, xdog_epsilon, xdog_phi
- morph_close_kernel, min_blob_area
- min_arc_length, min_contour_area, simplify_epsilon, min_contour_points
