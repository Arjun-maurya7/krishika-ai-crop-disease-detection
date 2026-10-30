"""
backend/utils/image_utils.py  —  Krishika AI CSE494 MongoDB Project
Image validation and decoding utilities.
"""

import logging
from pathlib import Path

import cv2
import numpy as np

logger = logging.getLogger(__name__)

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
MAX_DIMENSION      = 4096  # pixels


def validate_image_bytes(contents: bytes, content_type: str, max_mb: float = 10.0) -> None:
    """
    Validate uploaded image bytes.

    Raises:
        ValueError: if validation fails (caller should convert to HTTP 400)
    """
    max_bytes = int(max_mb * 1024 * 1024)
    if len(contents) > max_bytes:
        raise ValueError(f"Image exceeds {max_mb} MB limit ({len(contents) / 1e6:.1f} MB received).")

    allowed = {"image/jpeg", "image/png", "image/webp"}
    if content_type not in allowed:
        raise ValueError(f"Unsupported content type '{content_type}'. Allowed: {', '.join(allowed)}")


def decode_image(contents: bytes) -> np.ndarray:
    """
    Decode image bytes to a BGR numpy array using OpenCV.

    Raises:
        ValueError: if image cannot be decoded
    """
    arr = np.frombuffer(contents, dtype=np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("Could not decode image. Ensure it is a valid JPEG or PNG.")

    h, w = img.shape[:2]
    if h > MAX_DIMENSION or w > MAX_DIMENSION:
        logger.warning("Large image %dx%d — will be resized by VGG19 preprocessing.", w, h)

    return img
