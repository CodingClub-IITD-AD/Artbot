"""Scale image-space paths to the physical work area and clip to bounds."""

import numpy as np
from typing import List


def scale_and_clip(
    paths: List[np.ndarray],
    image_width: int,
    image_height: int,
    config: dict,
) -> List[np.ndarray]:
    """
    Scale pixel-coordinate paths into millimetres, centre them in the
    work area, and hard-clip to the safe zone.

    The image is scaled uniformly (aspect-ratio preserved) to fit
    inside the work area, then offset by the buffer.
    """
    machine = config.get("machine", {})
    buf = machine.get("buffer_mm", 50)
    wa_w = machine.get("work_area_width_mm", 1700)
    wa_h = machine.get("work_area_height_mm", 1100)

    # Uniform scale to fit
    scale = min(wa_w / image_width, wa_h / image_height)

    # Centre within the work area
    scaled_w = image_width * scale
    scaled_h = image_height * scale
    offset_x = buf + (wa_w - scaled_w) / 2
    offset_y = buf + (wa_h - scaled_h) / 2

    result: List[np.ndarray] = []
    for path in paths:
        scaled = path * scale
        scaled[:, 0] += offset_x
        scaled[:, 1] += offset_y

        # Hard-clip to safe zone
        scaled[:, 0] = np.clip(scaled[:, 0], buf, buf + wa_w)
        scaled[:, 1] = np.clip(scaled[:, 1], buf, buf + wa_h)

        result.append(scaled)

    return result
