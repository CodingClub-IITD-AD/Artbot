#!/usr/bin/env python3
"""
ArtBot Image-to-GCode Converter

Usage:
    python scripts/convert.py input.jpg -o output.gcode
    python scripts/convert.py input.jpg --mode sketch
    python scripts/convert.py input.jpg --mode photo --feed-rate 2000
"""

import argparse
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from artbot.image_processing.preprocess import load_image, detect_edges
from artbot.image_processing.trace import extract_contours, simplify_contours
from artbot.gcode_generation.clipping import scale_and_clip
from artbot.gcode_generation.path_sorting import sort_paths_nearest
from artbot.gcode_generation.generator import generate_gcode
from artbot.utils.config_loader import load_config


def main():
    parser = argparse.ArgumentParser(
        description="Convert an image to plotter G-Code",
    )
    parser.add_argument("image", help="Path to input image (JPEG/PNG)")
    parser.add_argument("-o", "--output", default=None,
                        help="Output .gcode file (default: <image_name>.gcode)")
    parser.add_argument("--mode", choices=["auto", "sketch", "photo"],
                        default="auto", help="Processing mode (default: auto)")
    parser.add_argument("--feed-rate", type=int, default=None,
                        help="Override drawing feed rate (mm/min)")
    parser.add_argument("--config", default=None,
                        help="Path to machine.yaml")
    parser.add_argument("--epsilon", type=float, default=None,
                        help="Path simplification tolerance (mm)")
    args = parser.parse_args()

    # Load config
    config = load_config(args.config)

    # CLI overrides
    if args.feed_rate:
        config["motion"]["draw_feed_rate"] = args.feed_rate
    if args.epsilon:
        config["processing"]["simplify_epsilon"] = args.epsilon

    # Default output path
    if args.output is None:
        base = os.path.splitext(os.path.basename(args.image))[0]
        args.output = f"{base}.gcode"

    # --- Pipeline ---
    print(f"[1/5] Loading image: {args.image}")
    gray = load_image(args.image)
    h, w = gray.shape[:2]
    print(f"       Size: {w} x {h} px")

    print(f"[2/5] Detecting edges (mode: {args.mode})")
    binary = detect_edges(gray, mode=args.mode, config=config)

    print("[3/5] Extracting contours")
    contours = extract_contours(binary)
    print(f"       Found {len(contours)} raw contours")

    print("[4/5] Scaling, simplifying & sorting paths")
    proc = config.get("processing", {})
    epsilon = proc.get("simplify_epsilon", 1.5)
    min_pts = proc.get("min_contour_points", 3)

    paths = scale_and_clip(contours, w, h, config)
    paths = simplify_contours(paths, epsilon=epsilon, min_points=min_pts)
    paths = sort_paths_nearest(paths)
    print(f"       {len(paths)} paths after processing")

    print("[5/5] Generating G-Code")
    gcode = generate_gcode(paths, config,
                           source_name=os.path.basename(args.image))

    with open(args.output, "w") as f:
        f.write(gcode)

    n_lines = gcode.count("\n") + 1
    print(f"\n Done  {args.output}  ({n_lines} lines)")


if __name__ == "__main__":
    main()
