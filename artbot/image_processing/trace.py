"""Contour extraction and simplification."""

import cv2
import numpy as np
from typing import List


def extract_contours(binary: np.ndarray) -> List[np.ndarray]:
    """
    Find contours in a binary edge image.

    Returns a list of Nx2 numpy arrays where each row is [x, y]
    in pixel coordinates.
    """
    contours, _ = cv2.findContours(
        binary, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE,
    )
    # Reshape from OpenCV's (N, 1, 2) → (N, 2)
    return [c.reshape(-1, 2).astype(np.float64) for c in contours]


def simplify_contours(
    paths: List[np.ndarray],
    epsilon: float = 2.0,
    min_points: int = 3,
) -> List[np.ndarray]:
    """
    Simplify contour paths with Douglas-Peucker.

    Parameters
    ----------
    paths : list of Nx2 arrays
        Paths in the final coordinate space (e.g. mm).
    epsilon : float
        Simplification tolerance (same units as the paths).
    min_points : int
        Discard paths with fewer points after simplification.
    """
    simplified = []
    for path in paths:
        approx = cv2.approxPolyDP(
            path.reshape(-1, 1, 2).astype(np.float32),
            epsilon,
            closed=False,
        )
        pts = approx.reshape(-1, 2).astype(np.float64)
        if len(pts) >= min_points:
            simplified.append(pts)
    return simplified
