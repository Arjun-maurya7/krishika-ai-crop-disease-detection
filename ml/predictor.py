# -*- coding: utf-8 -*-
"""
ml/predictor.py  —  Krishika AI CSE494 MongoDB Version
ML inference service — wraps the existing VGG19 + per-crop SVM pipeline.

Copied from the original backend/ml/predictor.py and adapted:
  - Import paths updated to use the new ml/ package
  - OUTPUT_ROOT now points to trained_models/ inside this project
  - Everything else identical (same VGG19 + SVM logic)

Design:
  - VGG19 feature extractor is loaded once and cached (singleton)
  - SVM models are loaded on-demand per crop and cached
  - Confidence is estimated via decision_function scores
  - Low-confidence predictions are flagged with is_uncertain=True
"""

from __future__ import annotations

import logging
import os
import threading
from dataclasses import dataclass

import cv2
import numpy as np

from ml.class_mappings import (
    CLASS_MAPPINGS,
    CONFIDENCE_THRESHOLD,
    LOW_ACCURACY_CROPS,
)
from ml.disease_db import get_disease_info

logger = logging.getLogger(__name__)

# ── Paths ─────────────────────────────────────────────────────────────────────
# This file lives at  <project>/ml/predictor.py
# trained models are at  <project>/trained_models/<Crop>/<Crop>_model.pkl
BASE_DIR    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_ROOT = os.path.join(BASE_DIR, "trained_models")
IMG_SIZE    = 224

# ── Singleton state ───────────────────────────────────────────────────────────
_lock              = threading.Lock()
_feature_extractor = None
_model_ready       = False
_loaded_svms: dict = {}


@dataclass
class PredictionResult:
    crop: str
    disease: str
    confidence: float       # 0.0 – 1.0
    is_uncertain: bool
    severity: str           # "healthy" | "medium" | "high"
    cause: str
    remedy: str
    impact: str
    symptoms: list[str]
    preventive_measures: list[str]
    uncertainty_message: str | None = None


# ── Model loading ─────────────────────────────────────────────────────────────

def _load_feature_extractor() -> None:
    """Build and cache the VGG19 feature extractor (frozen)."""
    global _feature_extractor, _model_ready

    import tensorflow as tf
    from tensorflow.keras.applications.vgg19 import VGG19
    from tensorflow.keras.layers import GlobalAveragePooling2D
    from tensorflow.keras.models import Model

    tf.get_logger().setLevel("ERROR")
    os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "3")
    os.environ.setdefault("TF_ENABLE_ONEDNN_OPTS", "0")

    logger.info("Loading VGG19 feature extractor …")
    base = VGG19(weights="imagenet", include_top=False,
                 input_shape=(IMG_SIZE, IMG_SIZE, 3))
    base.trainable = False
    x = GlobalAveragePooling2D()(base.output)
    _feature_extractor = Model(inputs=base.input, outputs=x)
    _model_ready = True
    logger.info("VGG19 feature extractor ready.")


def _ensure_model_loaded() -> None:
    """Ensure VGG19 is loaded; thread-safe double-checked locking."""
    global _model_ready
    if not _model_ready:
        with _lock:
            if not _model_ready:
                _load_feature_extractor()


def warmup() -> None:
    """Public helper — call in a background thread to pre-warm the model."""
    _ensure_model_loaded()


def _get_svm(crop: str):
    """Load and cache the SVM model for a given crop folder name."""
    if crop in _loaded_svms:
        return _loaded_svms[crop]

    import joblib

    candidates = [crop]
    for folder in os.listdir(OUTPUT_ROOT):
        if folder.lower() == crop.lower() and folder != crop:
            candidates.append(folder)

    for candidate in candidates:
        model_path = os.path.join(OUTPUT_ROOT, candidate, f"{candidate}_model.pkl")
        if os.path.exists(model_path):
            try:
                model = joblib.load(model_path)
                _loaded_svms[crop] = model
                logger.info("Loaded SVM for %s from %s", crop, model_path)
                return model
            except Exception as exc:
                logger.error("Failed to load SVM for %s: %s", crop, exc)
                return None

    logger.warning("No SVM model found for crop: %s", crop)
    return None


# ── Preprocessing ─────────────────────────────────────────────────────────────

def _preprocess(image: np.ndarray) -> np.ndarray:
    """
    Resize image to 224×224 and apply VGG19 preprocessing.
    Accepts BGR (cv2) or RGB numpy arrays.
    """
    from tensorflow.keras.applications.vgg19 import preprocess_input

    img_resized = cv2.resize(image, (IMG_SIZE, IMG_SIZE))
    img_batch   = np.expand_dims(img_resized.astype(float), axis=0)
    return preprocess_input(img_batch)


def _estimate_confidence(svm, features: np.ndarray) -> tuple[int, float]:
    """
    Estimate confidence from SVM decision_function scores.

    For binary SVM: raw score is a signed distance.
    For multi-class (OvO): returns the class with the highest vote count
    and normalises the max decision score as a proxy confidence.

    Returns:
        (predicted_class_index, confidence_0_to_1)
    """
    pred_idx = int(svm.predict(features)[0])

    try:
        scores = svm.decision_function(features)[0]
        scores_shifted = scores - scores.max()
        exp_scores     = np.exp(scores_shifted)
        confidence     = float(exp_scores[pred_idx] / exp_scores.sum())
    except Exception:
        try:
            proba      = svm.predict_proba(features)[0]
            confidence = float(proba.max())
        except Exception:
            confidence = 0.5  # neutral fallback

    return pred_idx, confidence


# ── Main prediction function ──────────────────────────────────────────────────

def predict(crop: str, image: np.ndarray) -> PredictionResult:
    """
    Run end-to-end disease prediction for the given crop and leaf image.

    Args:
        crop:  Crop folder name matching keys in CLASS_MAPPINGS (e.g. "Tomato")
        image: numpy array (H×W×3), BGR or RGB

    Returns:
        PredictionResult dataclass with all diagnosis fields

    Raises:
        ValueError: if crop is unsupported or model is unavailable
    """
    if crop not in CLASS_MAPPINGS:
        raise ValueError(f"Unsupported crop: '{crop}'. Supported: {list(CLASS_MAPPINGS.keys())}")

    if image is None or not isinstance(image, np.ndarray) or image.size == 0:
        raise ValueError("Invalid image: expected a non-empty numpy array.")
    if image.ndim not in (2, 3):
        raise ValueError(f"Invalid image dimensions: {image.ndim}D. Expected 2D or 3D array.")

    _ensure_model_loaded()

    svm = _get_svm(crop)
    if svm is None:
        raise ValueError(f"SVM model not available for '{crop}'.")

    preprocessed = _preprocess(image)
    features     = _feature_extractor.predict(preprocessed, verbose=0)

    pred_idx, confidence = _estimate_confidence(svm, features)

    class_list = CLASS_MAPPINGS[crop]
    if pred_idx < len(class_list):
        disease_name = class_list[pred_idx]
    else:
        disease_name = f"Unknown Class ({pred_idx})"
        confidence   = 0.0

    is_uncertain    = (confidence < CONFIDENCE_THRESHOLD) or (crop in LOW_ACCURACY_CROPS)
    uncertainty_msg = None
    if is_uncertain:
        if crop in LOW_ACCURACY_CROPS:
            uncertainty_msg = (
                f"⚠️ Note: The model for {crop} has lower overall accuracy (65%). "
                "This prediction should be verified with a local agronomist before treatment."
            )
        else:
            uncertainty_msg = (
                f"⚠️ Low confidence ({confidence:.0%}). The model is uncertain about this prediction. "
                "Consider re-uploading a clearer image or consulting a Krishi Vigyan Kendra."
            )

    disease_info = get_disease_info(crop, disease_name)

    return PredictionResult(
        crop                = crop,
        disease             = disease_name,
        confidence          = round(confidence, 4),
        is_uncertain        = is_uncertain,
        severity            = disease_info["severity"],
        cause               = disease_info["cause"],
        remedy              = disease_info["remedy"],
        impact              = disease_info["impact"],
        symptoms            = disease_info["symptoms"],
        preventive_measures = disease_info["preventive_measures"],
        uncertainty_message = uncertainty_msg,
    )


def list_available_crops() -> list[str]:
    """Return list of crops for which SVM models exist on disk."""
    available = []
    if not os.path.exists(OUTPUT_ROOT):
        return list(CLASS_MAPPINGS.keys())
    for folder in os.listdir(OUTPUT_ROOT):
        folder_path = os.path.join(OUTPUT_ROOT, folder)
        if os.path.isdir(folder_path):
            model_file = os.path.join(folder_path, f"{folder}_model.pkl")
            if os.path.exists(model_file) and folder in CLASS_MAPPINGS:
                available.append(folder)
    return sorted(available)
