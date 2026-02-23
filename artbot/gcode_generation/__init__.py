"""G-Code generation, path optimization, and boundary clipping."""
from .generator import generate_gcode
from .path_sorting import sort_paths_nearest
from .clipping import scale_and_clip
