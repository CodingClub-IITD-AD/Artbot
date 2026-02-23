"""Path sorting to minimise pen-up travel (air time)."""

import numpy as np
from typing import List


def sort_paths_nearest(paths: List[np.ndarray]) -> List[np.ndarray]:
    """
    Greedy nearest-neighbour sort.

    Starting from (0, 0), always jump to the path whose start (or end)
    point is closest to the current pen position.  Paths are reversed
    when their end point is nearer than their start.
    """
    if not paths:
        return []

    remaining = list(range(len(paths)))
    sorted_paths: List[np.ndarray] = []
    current_pos = np.array([0.0, 0.0])

    while remaining:
        best_idx = None
        best_dist = float("inf")
        best_reversed = False

        for i in remaining:
            p = paths[i]
            d_start = np.linalg.norm(current_pos - p[0])
            d_end = np.linalg.norm(current_pos - p[-1])

            if d_start < best_dist:
                best_dist = d_start
                best_idx = i
                best_reversed = False
            if d_end < best_dist:
                best_dist = d_end
                best_idx = i
                best_reversed = True

        remaining.remove(best_idx)
        chosen = paths[best_idx]
        if best_reversed:
            chosen = chosen[::-1]
        sorted_paths.append(chosen)
        current_pos = chosen[-1].copy()

    return sorted_paths
