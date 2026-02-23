#!/usr/bin/env python3
"""
ArtBot Interactive Parameter Tuner

Drag sliders to adjust edge detection in real time.
Press 's' to save settings + generate G-Code.
Press 'q' to quit without saving.

Usage:
    python scripts/tune.py image.png
    python scripts/tune.py image.png -o output.gcode
"""

import argparse
import os
import sys

import cv2
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from artbot.utils.config_loader import load_config


def xdog(gray, sigma, k, p, epsilon, phi):
    """XDoG sketch extraction."""
    img = gray.astype(np.float64) / 255.0
    g1 = cv2.GaussianBlur(img, (0, 0), max(sigma, 0.1))
    g2 = cv2.GaussianBlur(img, (0, 0), max(sigma * k, 0.2))
    diff = g1 - p * g2
    result = np.where(
        diff >= epsilon,
        1.0,
        1.0 + np.tanh(phi * (diff - epsilon)),
    )
    result = (np.clip(result, 0, 1) * 255).astype(np.uint8)
    _, binary = cv2.threshold(result, 240, 255, cv2.THRESH_BINARY_INV)
    return binary


def remove_small_blobs(binary, min_area):
    """Remove connected components smaller than min_area."""
    if min_area <= 0:
        return binary
    n_labels, labels, stats, _ = cv2.connectedComponentsWithStats(binary, 8)
    cleaned = np.zeros_like(binary)
    for i in range(1, n_labels):
        if stats[i, cv2.CC_STAT_AREA] >= min_area:
            cleaned[labels == i] = 255
    return cleaned


def process(gray, params):
    """Full processing pipeline with given params."""
    h, w = gray.shape[:2]

    # Downscale
    sf = params["downscale"] / 100.0
    if sf < 1.0:
        small = cv2.resize(gray, None, fx=sf, fy=sf,
                           interpolation=cv2.INTER_AREA)
    else:
        small = gray.copy()

    # CLAHE
    clahe = cv2.createCLAHE(
        clipLimit=params["clahe_clip"] / 10.0,
        tileGridSize=(8, 8),
    )
    enhanced = clahe.apply(small)

    # XDoG
    binary = xdog(
        enhanced,
        sigma=params["sigma"] / 100.0,
        k=params["k"],
        p=params["p"] / 100.0,
        epsilon=(params["epsilon"] - 50) / 100.0,
        phi=params["phi"] / 10.0,
    )

    # Morphological close
    ck = params["morph_close"]
    if ck > 0:
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (ck, ck))
        binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)

    # Remove small blobs
    binary = remove_small_blobs(binary, params["min_blob"])

    # Scale back up
    if sf < 1.0:
        binary = cv2.resize(binary, (w, h),
                            interpolation=cv2.INTER_NEAREST)

    return binary


def nothing(_):
    pass


def main():
    parser = argparse.ArgumentParser(
        description="Interactive edge detection tuner",
    )
    parser.add_argument("image", help="Input image path")
    parser.add_argument("-o", "--output", default=None,
                        help="Output .gcode file (generated on 's' press)")
    parser.add_argument("--config", default=None, help="Path to machine.yaml")
    args = parser.parse_args()

    config = load_config(args.config)
    proc = config.get("processing", {})

    gray = cv2.imread(args.image, cv2.IMREAD_GRAYSCALE)
    if gray is None:
        print(f"Error: cannot load {args.image}")
        sys.exit(1)

    # Resize preview to fit screen
    max_h = 700
    scale = min(1.0, max_h / gray.shape[0])
    preview_size = (int(gray.shape[1] * scale), int(gray.shape[0] * scale))

    win = "ArtBot Tuner  |  's' = save & generate gcode  |  'q' = quit"
    cv2.namedWindow(win, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(win, preview_size[0], preview_size[1])

    # Create trackbars with initial values from config
    cv2.createTrackbar("Downscale %",  win, int(proc.get("downscale_factor", 0.5) * 100), 100, nothing)
    cv2.createTrackbar("CLAHE Clip",   win, int(proc.get("clahe_clip", 2.5) * 10), 50, nothing)
    cv2.createTrackbar("Sigma x100",   win, int(proc.get("xdog_sigma", 0.5) * 100), 300, nothing)
    cv2.createTrackbar("K",            win, int(proc.get("xdog_k", 200)), 500, nothing)
    cv2.createTrackbar("P x100",       win, int(proc.get("xdog_p", 0.98) * 100), 100, nothing)
    cv2.createTrackbar("Epsilon+50",   win, int((proc.get("xdog_epsilon", -0.1) + 0.5) * 100), 100, nothing)
    cv2.createTrackbar("Phi x10",      win, int(proc.get("xdog_phi", 10.0) * 10), 200, nothing)
    cv2.createTrackbar("Morph Close",  win, proc.get("morph_close_kernel", 2), 10, nothing)
    cv2.createTrackbar("Min Blob",     win, proc.get("min_blob_area", 100), 500, nothing)

    print("\n  ArtBot Tuner")
    print("  ────────────")
    print("  Drag sliders to adjust edge detection.")
    print("  Press 's' to save settings and generate G-Code.")
    print("  Press 'q' to quit.\n")

    while True:
        params = {
            "downscale":   max(10, cv2.getTrackbarPos("Downscale %", win)),
            "clahe_clip":  max(1, cv2.getTrackbarPos("CLAHE Clip", win)),
            "sigma":       max(10, cv2.getTrackbarPos("Sigma x100", win)),
            "k":           max(1, cv2.getTrackbarPos("K", win)),
            "p":           max(1, cv2.getTrackbarPos("P x100", win)),
            "epsilon":     cv2.getTrackbarPos("Epsilon+50", win),
            "phi":         max(1, cv2.getTrackbarPos("Phi x10", win)),
            "morph_close": cv2.getTrackbarPos("Morph Close", win),
            "min_blob":    cv2.getTrackbarPos("Min Blob", win),
        }

        binary = process(gray, params)

        # Show side by side: original | edges
        gray_resized = cv2.resize(gray, preview_size)
        edge_resized = cv2.resize(binary, preview_size)
        # Invert edges for display (black lines on white, like paper)
        display_edges = cv2.bitwise_not(edge_resized)
        combined = np.hstack([gray_resized, display_edges])
        cv2.imshow(win, combined)

        key = cv2.waitKey(100) & 0xFF

        if key == ord('q'):
            print("  Quit without saving.")
            break

        elif key == ord('s'):
            # Save params back to config
            real_params = {
                "downscale_factor": params["downscale"] / 100.0,
                "clahe_clip":      params["clahe_clip"] / 10.0,
                "xdog_sigma":      params["sigma"] / 100.0,
                "xdog_k":          params["k"],
                "xdog_p":          params["p"] / 100.0,
                "xdog_epsilon":    (params["epsilon"] - 50) / 100.0,
                "xdog_phi":        params["phi"] / 10.0,
                "morph_close_kernel": params["morph_close"],
                "min_blob_area":   params["min_blob"],
            }

            print("\n  Saved parameters:")
            for k, v in real_params.items():
                print(f"    {k}: {v}")

            # Update config processing section
            config["processing"].update(real_params)

            # Write updated YAML
            import yaml
            cfg_path = args.config
            if cfg_path is None:
                here = os.path.dirname(os.path.abspath(__file__))
                cfg_path = os.path.join(
                    os.path.dirname(here), "config", "machine.yaml")
            with open(cfg_path, "w") as f:
                yaml.dump(config, f, default_flow_style=False,
                          sort_keys=False)
            print(f"  Config saved: {cfg_path}")

            # Generate gcode
            cv2.destroyAllWindows()

            from artbot.image_processing.preprocess import load_image, detect_edges
            from artbot.image_processing.trace import extract_contours, simplify_contours
            from artbot.gcode_generation.clipping import scale_and_clip
            from artbot.gcode_generation.path_sorting import sort_paths_nearest
            from artbot.gcode_generation.generator import generate_gcode

            print("\n  Generating G-Code...")
            gray_full = load_image(args.image)
            h, w = gray_full.shape[:2]
            edges = detect_edges(gray_full, mode="photo", config=config)
            p = config.get("processing", {})
            contours = extract_contours(
                edges,
                min_arc_length=p.get("min_arc_length", 30),
                min_area=p.get("min_contour_area", 80),
            )
            paths = scale_and_clip(contours, w, h, config)
            paths = simplify_contours(
                paths,
                epsilon=p.get("simplify_epsilon", 1.5),
                min_points=p.get("min_contour_points", 3),
            )
            paths = sort_paths_nearest(paths)

            gcode = generate_gcode(
                paths, config,
                source_name=os.path.basename(args.image),
            )

            out = args.output
            if out is None:
                base = os.path.splitext(os.path.basename(args.image))[0]
                out = f"{base}.gcode"
            with open(out, "w") as f:
                f.write(gcode)

            n = gcode.count("\n") + 1
            print(f"  Done! {out}  ({n} lines, {len(paths)} paths)")
            print(f"\n  To simulate:  python scripts/simulate.py {out}")
            break

    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
