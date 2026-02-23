"""Contour extraction and simplification."""

import cv2
import numpy as np
from typing import List


def extract_contours(
    binary: np.ndarray,
    min_arc_length: float = 20.0,
    min_area: float = 50.0,
) -> List[np.ndarray]:
    """
    Find contours in a binary edge image, filtering out noise.

    Parameters
    ----------
    binary : ndarray
        Binary edge image (white edges on black).
    min_arc_length : float
        Discard contours shorter than this (in pixels).
    min_area : float
        Discard contours whose bounding box area is smaller than this.

    Returns a list of Nx2 numpy arrays where each row is [x, y]
    in pixel coordinates.
    """
    contours, _ = cv2.findContours(
        binary, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE,
    )

    filtered = []
    for c in contours:
        # Skip tiny noise contours
        arc = cv2.arcLength(c, closed=False)
        if arc < min_arc_length:
            continue

        # Skip contours with negligible bounding area
        _, _, bw, bh = cv2.boundingRect(c)
        if bw * bh < min_area:
            continue

        filtered.append(c.reshape(-1, 2).astype(np.float64))

    return filtered


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
