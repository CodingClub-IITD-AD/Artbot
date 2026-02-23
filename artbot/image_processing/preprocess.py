"""Image loading and edge detection for the ArtBot pipeline."""

import cv2
import numpy as np


def load_image(path: str) -> np.ndarray:
    """Load an image file and convert to grayscale."""
    img = cv2.imread(path)
    if img is None:
        raise FileNotFoundError(f"Could not load image: {path}")
    return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)


def detect_edges(
    gray: np.ndarray,
    mode: str = "auto",
    config: dict = None,
) -> np.ndarray:
    """
    Convert a grayscale image to a binary edge map.

    Modes
    -----
    auto   – heuristic pick between sketch and photo
    sketch – simple threshold (clean line art / ink drawings)
    photo  – Canny edge detection (photographs)
    """
    if config is None:
        config = {}

    proc = config.get("processing", {})

    if mode == "auto":
        mode = _detect_image_type(gray)
        print(f"       Auto-detected mode: {mode}")

    if mode == "sketch":
        thresh_val = proc.get("threshold", 128)
        # Invert so drawn lines become white-on-black
        _, binary = cv2.threshold(gray, thresh_val, 255, cv2.THRESH_BINARY_INV)
    else:  # photo
        blur_k = proc.get("blur_kernel", 5)
        low = proc.get("canny_low", 50)
        high = proc.get("canny_high", 150)
        blurred = cv2.GaussianBlur(gray, (blur_k, blur_k), 0)
        binary = cv2.Canny(blurred, low, high)

    return binary


def _detect_image_type(gray: np.ndarray) -> str:
    """
    Heuristic: if 85%+ of pixels are near-white or near-black,
    it's likely a sketch/line-art image.
    """
    hist = cv2.calcHist([gray], [0], None, [256], [0, 256]).flatten()
    total = hist.sum()
    extreme = hist[:50].sum() + hist[200:].sum()
    ratio = extreme / total
    return "sketch" if ratio > 0.85 else "photo"
