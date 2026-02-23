"""Generate plotter G-Code from processed paths."""

from datetime import datetime
from typing import List

import numpy as np


def generate_gcode(
    paths: List[np.ndarray],
    config: dict,
    source_name: str = "unknown",
) -> str:
    """
    Convert a list of mm-coordinate paths into a G-Code string.

    Each path becomes:
        pen-up -> rapid-move to start -> pen-down -> draw segments -> pen-up
    """
    motion = config.get("motion", {})
    pen_cfg = config.get("pen", {})

    feed = motion.get("draw_feed_rate", 3000)
    rapid = motion.get("rapid_feed_rate", 5000)
    pen_down_cmd = pen_cfg.get("down_command", "M3 S90")
    pen_up_cmd = pen_cfg.get("up_command", "M5")
    dwell_s = pen_cfg.get("settle_time_ms", 150) / 1000

    lines = []

    # Header
    lines.append("; ArtBot G-Code")
    lines.append(f"; Generated: {datetime.now().isoformat()}")
    lines.append(f"; Source: {source_name}")
    lines.append(f"; Paths: {len(paths)}")
    lines.append("")
    lines.append("G21 ; Units: mm")
    lines.append("G90 ; Absolute positioning")
    lines.append(f"{pen_up_cmd} ; Pen up")
    lines.append(f"G4 P{dwell_s:.3f} ; Settle")
    lines.append("")

    total_draw = 0.0
    total_travel = 0.0
    current = np.array([0.0, 0.0])

    for i, path in enumerate(paths):
        if len(path) < 2:
            continue

        start = path[0]
        total_travel += np.linalg.norm(start - current)

        lines.append(f"; --- Path {i + 1}/{len(paths)} ({len(path)} pts) ---")
        lines.append(f"G0 X{start[0]:.2f} Y{start[1]:.2f} F{rapid} ; Travel")
        lines.append(f"{pen_down_cmd} ; Pen down")
        lines.append(f"G4 P{dwell_s:.3f} ; Settle")

        for j in range(1, len(path)):
            x, y = path[j]
            total_draw += np.linalg.norm(path[j] - path[j - 1])
            lines.append(f"G1 X{x:.2f} Y{y:.2f} F{feed}")

        lines.append(f"{pen_up_cmd} ; Pen up")
        lines.append(f"G4 P{dwell_s:.3f} ; Settle")
        lines.append("")
        current = path[-1].copy()

    # Footer
    lines.append("; Return home")
    lines.append(f"G0 X0.00 Y0.00 F{rapid}")
    lines.append(pen_up_cmd)
    lines.append("M2 ; Program end")
    lines.append("")
    est_min = total_draw / feed + total_travel / rapid
    lines.append(f"; Draw distance:   {total_draw:.0f} mm")
    lines.append(f"; Travel distance: {total_travel:.0f} mm")
    lines.append(f"; Estimated time:  {est_min:.1f} min")

    return "\n".join(lines)
