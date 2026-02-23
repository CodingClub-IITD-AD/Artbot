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
    photo  – XDoG sketch-style extraction (best for plotter output)
    """
    if config is None:
        config = {}

    proc = config.get("processing", {})

    if mode == "auto":
        mode = _detect_image_type(gray)
        print(f"       Auto-detected mode: {mode}")

    if mode == "sketch":
        binary = _process_sketch(gray, proc)
    else:
        binary = _process_photo(gray, proc)

    return binary


# ── Sketch mode ─────────────────────────────────────────────

def _process_sketch(gray: np.ndarray, proc: dict) -> np.ndarray:
    """Simple threshold for clean line art."""
    thresh_val = proc.get("threshold", 128)
    _, binary = cv2.threshold(gray, thresh_val, 255, cv2.THRESH_BINARY_INV)
    return binary


# ── Photo mode ──────────────────────────────────────────────

def _process_photo(gray: np.ndarray, proc: dict) -> np.ndarray:
    """
    Multi-stage pipeline for converting photographs to clean outlines.

    1. Downscale (reduces noise / fine texture dramatically)
    2. CLAHE contrast enhancement
    3. XDoG (Extended Difference of Gaussians) for sketch-like lines
    4. Morphological cleanup
    """
    # --- 0. Downscale to remove fine detail ---
    scale_factor = proc.get("downscale_factor", 0.5)
    h, w = gray.shape[:2]
    if scale_factor < 1.0:
        small = cv2.resize(
            gray, None, fx=scale_factor, fy=scale_factor,
            interpolation=cv2.INTER_AREA,
        )
    else:
        small = gray.copy()

    # --- 1. CLAHE contrast enhancement ---
    clahe_clip = proc.get("clahe_clip", 2.5)
    clahe_grid = proc.get("clahe_grid", 8)
    clahe = cv2.createCLAHE(
        clipLimit=clahe_clip,
        tileGridSize=(clahe_grid, clahe_grid),
    )
    enhanced = clahe.apply(small)

    # --- 2. XDoG for sketch-like line extraction ---
    binary = _xdog(
        enhanced,
        sigma=proc.get("xdog_sigma", 0.5),
        k=proc.get("xdog_k", 200),
        p=proc.get("xdog_p", 0.98),
        epsilon=proc.get("xdog_epsilon", -0.1),
        phi=proc.get("xdog_phi", 10.0),
    )

    # --- 3. Morphological cleanup ---
    close_k = proc.get("morph_close_kernel", 2)
    if close_k > 0:
        kernel = cv2.getStructuringElement(
            cv2.MORPH_RECT, (close_k, close_k),
        )
        binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)

    # --- 4. Remove tiny noise blobs ---
    min_blob = proc.get("min_blob_area", 100)
    if min_blob > 0:
        binary = _remove_small_blobs(binary, min_blob)

    # --- 5. Scale back up to original size ---
    if scale_factor < 1.0:
        binary = cv2.resize(
            binary, (w, h), interpolation=cv2.INTER_NEAREST,
        )

    return binary


def _xdog(
    gray: np.ndarray,
    sigma: float = 0.5,
    k: float = 200,
    p: float = 0.98,
    epsilon: float = -0.1,
    phi: float = 10.0,
) -> np.ndarray:
    """
    Extended Difference of Gaussians (XDoG).

    Produces sketch-like line art from a grayscale image.
    Much better than Canny for plotter output because it captures
    structural edges and ignores fine texture.

    Parameters
    ----------
    sigma    : base Gaussian sigma (controls edge scale)
    k        : ratio between the two Gaussian sigmas (large = coarser)
    p        : blend factor (controls how much the wider blur subtracts)
    epsilon  : threshold for the soft step function
    phi      : sharpness of the soft threshold (higher = crisper lines)
    """
    img = gray.astype(np.float64) / 255.0

    # Two Gaussian blurs at different scales
    g1 = cv2.GaussianBlur(img, (0, 0), sigma)
    g2 = cv2.GaussianBlur(img, (0, 0), sigma * k)

    # DoG with asymmetric blend
    diff = g1 - p * g2

    # Soft threshold: produces clean black lines on white
    result = np.where(
        diff >= epsilon,
        1.0,
        1.0 + np.tanh(phi * (diff - epsilon)),
    )

    # Convert to binary (white edges on black background)
    result = (np.clip(result, 0, 1) * 255).astype(np.uint8)
    _, binary = cv2.threshold(result, 240, 255, cv2.THRESH_BINARY_INV)

    return binary


def _remove_small_blobs(binary: np.ndarray, min_area: int) -> np.ndarray:
    """Remove connected components smaller than min_area pixels."""
    n_labels, labels, stats, _ = cv2.connectedComponentsWithStats(
        binary, connectivity=8,
    )
    cleaned = np.zeros_like(binary)
    for i in range(1, n_labels):  # skip background (label 0)
        if stats[i, cv2.CC_STAT_AREA] >= min_area:
            cleaned[labels == i] = 255
    return cleaned


# ── Auto-detection ──────────────────────────────────────────

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
