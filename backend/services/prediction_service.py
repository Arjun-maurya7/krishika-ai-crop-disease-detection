"""
backend/services/prediction_service.py  —  Krishika AI CSE494 MongoDB Project

Thin async-friendly wrapper around the synchronous ML predictor.

Since PyMongo is also synchronous, the whole detect() function runs in
a thread-pool executor via asyncio.get_event_loop().run_in_executor().
The FastAPI route awaits the executor future, keeping the ASGI loop unblocked.
"""

import asyncio
import logging
from functools import partial
from typing import Optional

import numpy as np

from ml.predictor import PredictionResult, predict

logger = logging.getLogger(__name__)


async def run_prediction(crop: str, image: np.ndarray) -> PredictionResult:
    """
    Run ML inference in a thread-pool executor so it does not block the
    ASGI event loop.

    Args:
        crop:  Crop key (e.g. "Tomato")
        image: Decoded numpy array (BGR)

    Returns:
        PredictionResult dataclass

    Raises:
        ValueError: for unsupported crop or missing model
    """
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, partial(predict, crop, image))
    logger.info("Prediction complete: %s → %s (%.1f%%)",
                crop, result.disease, result.confidence * 100)
    return result
