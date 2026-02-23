#!/usr/bin/env python3
"""
ArtBot G-Code Simulator

Visualises G-Code output as an animated pen plotter.

Usage:
    python scripts/simulate.py output.gcode
    python scripts/simulate.py output.gcode --speed 10
    python scripts/simulate.py output.gcode --no-animate
"""

import argparse
import os
import sys

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.patches import Rectangle

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from artbot.utils.config_loader import load_config


# ── G-Code Parser ───────────────────────────────────────────

def parse_gcode(filepath: str) -> list:
    """
    Parse a G-Code file into an ordered list of moves.

    Returns list of dicts with keys:
        type   – "draw" | "travel" | "pen_up" | "pen_down"
        x0, y0 – start position  (movement types only)
        x1, y1 – end position    (movement types only)
        feed   – feed rate        (movement types only)
    """
    moves = []
    cx, cy = 0.0, 0.0
    pen_down = False

    with open(filepath, "r") as f:
        for raw in f:
            line = raw.split(";")[0].strip()
            if not line:
                continue

            if line.startswith("M3"):
                pen_down = True
                moves.append({"type": "pen_down"})
                continue
            if line.startswith("M5"):
                pen_down = False
                moves.append({"type": "pen_up"})
                continue
            if line.startswith("M2"):
                break
            if line.startswith("G4") or line.startswith("G21") or line.startswith("G90"):
                continue

            if line.startswith("G0") or line.startswith("G1"):
                x, y, feed = cx, cy, None
                for tok in line.split():
                    if tok.startswith("X"):
                        x = float(tok[1:])
                    elif tok.startswith("Y"):
                        y = float(tok[1:])
                    elif tok.startswith("F"):
                        feed = float(tok[1:])

                mtype = "draw" if (not line.startswith("G0") and pen_down) else "travel"
                moves.append({
                    "type": mtype,
                    "x0": cx, "y0": cy,
                    "x1": x,  "y1": y,
                    "feed": feed,
                })
                cx, cy = x, y

    return moves


# ── Segment helpers ─────────────────────────────────────────

def split_segments(moves):
    """Split moves into draw and travel segment lists (for stats)."""
    draw, travel = [], []
    for m in moves:
        if m["type"] == "draw":
            draw.append((m["x0"], m["y0"], m["x1"], m["y1"]))
        elif m["type"] == "travel":
            travel.append((m["x0"], m["y0"], m["x1"], m["y1"]))
    return draw, travel


def seg_dist(segs):
    return sum(np.hypot(s[2] - s[0], s[3] - s[1]) for s in segs)


# ── Static plot ─────────────────────────────────────────────

def show_static(moves, config):
    machine = config.get("machine", {})
    fw = machine.get("frame_width_mm", 1800)
    fh = machine.get("frame_height_mm", 1200)
    buf = machine.get("buffer_mm", 50)
    draw_segs, travel_segs = split_segments(moves)

    fig, ax = plt.subplots(figsize=(14, 9))
    ax.set_xlim(-30, fw + 30)
    ax.set_ylim(fh + 30, -30)
    ax.set_aspect("equal")
    ax.set_facecolor("#f5f5f0")
    ax.set_title("ArtBot — G-Code Preview", fontsize=14, fontweight="bold")
    ax.set_xlabel("X (mm)")
    ax.set_ylabel("Y (mm)")

    ax.add_patch(Rectangle((0, 0), fw, fh,
                            fill=False, edgecolor="#888", lw=2))
    ax.add_patch(Rectangle((buf, buf), fw - 2 * buf, fh - 2 * buf,
                            fill=False, edgecolor="#4CAF50", lw=1,
                            linestyle="--", alpha=0.7))

    for s in travel_segs:
        ax.plot([s[0], s[2]], [s[1], s[3]],
                color="#ccc", lw=0.3, linestyle=":")
    for s in draw_segs:
        ax.plot([s[0], s[2]], [s[1], s[3]],
                color="#1a1a2e", lw=0.8)

    dd = seg_dist(draw_segs)
    td = seg_dist(travel_segs)
    motion = config.get("motion", {})
    est = dd / motion.get("draw_feed_rate", 3000) + \
          td / motion.get("rapid_feed_rate", 5000)
    ax.text(fw / 2, fh + 18,
            f"Draw: {dd/1000:.1f}m  |  Travel: {td/1000:.1f}m  |"
            f"  Est: {est:.1f} min  |  Segments: {len(draw_segs)}",
            ha="center", fontsize=9, color="#666")

    plt.tight_layout()
    plt.show()


# ── Animated plot ───────────────────────────────────────────

def show_animated(moves, config, speed=5):
    machine = config.get("machine", {})
    fw = machine.get("frame_width_mm", 1800)
    fh = machine.get("frame_height_mm", 1200)
    buf = machine.get("buffer_mm", 50)

    move_cmds = [m for m in moves if m["type"] in ("draw", "travel")]
    total = len(move_cmds)
    if total == 0:
        print("No movement commands found.")
        return

    fig, ax = plt.subplots(figsize=(14, 9))
    ax.set_xlim(-30, fw + 30)
    ax.set_ylim(fh + 30, -30)
    ax.set_aspect("equal")
    ax.set_facecolor("#f5f5f0")
    ax.set_title("ArtBot — Simulation", fontsize=14, fontweight="bold")
    ax.set_xlabel("X (mm)")
    ax.set_ylabel("Y (mm)")

    ax.add_patch(Rectangle((0, 0), fw, fh,
                            fill=False, edgecolor="#888", lw=2))
    ax.add_patch(Rectangle((buf, buf), fw - 2 * buf, fh - 2 * buf,
                            fill=False, edgecolor="#4CAF50", lw=1,
                            linestyle="--", alpha=0.7))

    pen_dot, = ax.plot([], [], "o", color="#e74c3c", ms=6, zorder=10)
    progress = ax.text(fw / 2, -12, "", ha="center", fontsize=10,
                       color="#333")
    drawn_count = [0]
    step = max(1, speed)

    def init():
        pen_dot.set_data([], [])
        return [pen_dot, progress]

    def update(frame_num):
        target = min((frame_num + 1) * step, total)
        while drawn_count[0] < target:
            m = move_cmds[drawn_count[0]]
            if m["type"] == "draw":
                ax.plot([m["x0"], m["x1"]], [m["y0"], m["y1"]],
                        color="#1a1a2e", lw=0.8)
            else:
                ax.plot([m["x0"], m["x1"]], [m["y0"], m["y1"]],
                        color="#ddd", lw=0.3, linestyle=":")
            drawn_count[0] += 1

        if drawn_count[0] > 0:
            m = move_cmds[min(drawn_count[0] - 1, total - 1)]
            pen_dot.set_data([m["x1"]], [m["y1"]])

        pct = drawn_count[0] / total * 100
        if drawn_count[0] >= total:
            progress.set_text(f"Complete! ({total} segments)")
            pen_dot.set_data([], [])
        else:
            progress.set_text(
                f"Drawing... {pct:.0f}%  ({drawn_count[0]}/{total})")
        return [pen_dot, progress]

    n_frames = (total // step) + 2
    _anim = animation.FuncAnimation(
        fig, update, init_func=init,
        frames=n_frames, interval=30, blit=False, repeat=False,
    )
    plt.tight_layout()
    plt.show()


# ── CLI ─────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Simulate ArtBot G-Code")
    parser.add_argument("gcode", help="Path to .gcode file")
    parser.add_argument("--no-animate", action="store_true",
                        help="Static final result instead of animation")
    parser.add_argument("--speed", type=int, default=5,
                        help="Segments per animation frame (default: 5)")
    parser.add_argument("--config", default=None,
                        help="Path to machine.yaml")
    args = parser.parse_args()

    config = load_config(args.config)
    print(f"Parsing: {args.gcode}")
    moves = parse_gcode(args.gcode)
    draw_segs, travel_segs = split_segments(moves)

    dd = seg_dist(draw_segs)
    td = seg_dist(travel_segs)
    motion = config.get("motion", {})
    est = dd / motion.get("draw_feed_rate", 3000) + \
          td / motion.get("rapid_feed_rate", 5000)

    print(f"  Draw segments:   {len(draw_segs)}")
    print(f"  Travel segments: {len(travel_segs)}")
    print(f"  Draw distance:   {dd/1000:.2f} m")
    print(f"  Travel distance: {td/1000:.2f} m")
    print(f"  Estimated time:  {est:.1f} min")

    if args.no_animate:
        show_static(moves, config)
    else:
        show_animated(moves, config, speed=args.speed)


if __name__ == "__main__":
    main()
