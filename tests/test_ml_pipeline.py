"""
tests/test_ml_pipeline.py  —  Krishika AI CSE494 MongoDB Project
Tests for the ML prediction pipeline (no MongoDB required).
"""

import os
import sys
import pytest
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ml.class_mappings import CLASS_MAPPINGS, CONFIDENCE_THRESHOLD, LOW_ACCURACY_CROPS
from ml.predictor import list_available_crops, _preprocess


# ── Class mappings ────────────────────────────────────────────────────────────

def test_class_mappings_not_empty():
    assert len(CLASS_MAPPINGS) == 17, f"Expected 17 crops, got {len(CLASS_MAPPINGS)}"


def test_all_crops_have_diseases():
    for crop, diseases in CLASS_MAPPINGS.items():
        assert len(diseases) >= 2, f"{crop} has fewer than 2 disease classes."


def test_confidence_threshold_in_range():
    assert 0.0 < CONFIDENCE_THRESHOLD < 1.0


def test_low_accuracy_crops_exist():
    assert "Brinjal" in LOW_ACCURACY_CROPS


# ── Trained models on disk ────────────────────────────────────────────────────

def test_trained_models_exist():
    available = list_available_crops()
    assert len(available) > 0, "No trained SVM models found in trained_models/."
    print(f"\nAvailable crops: {available}")


def test_all_17_crops_have_models():
    available = list_available_crops()
    missing   = [c for c in CLASS_MAPPINGS if c not in available]
    assert missing == [], f"Missing models for: {missing}"


# ── Image preprocessing ───────────────────────────────────────────────────────

def test_preprocess_output_shape():
    """_preprocess must return (1, 224, 224, 3)."""
    img    = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
    result = _preprocess(img)
    assert result.shape == (1, 224, 224, 3), f"Unexpected shape: {result.shape}"


def test_preprocess_accepts_small_image():
    img    = np.random.randint(0, 255, (50, 50, 3), dtype=np.uint8)
    result = _preprocess(img)
    assert result.shape == (1, 224, 224, 3)


# ── Predict validation ────────────────────────────────────────────────────────

def test_predict_raises_on_invalid_crop():
    from ml.predictor import predict
    with pytest.raises(ValueError, match="Unsupported crop"):
        predict("InvalidCrop", np.zeros((100, 100, 3), dtype=np.uint8))


def test_predict_raises_on_empty_image():
    from ml.predictor import predict
    with pytest.raises(ValueError, match="Invalid image"):
        predict("Tomato", np.array([]))


# ── Disease DB ────────────────────────────────────────────────────────────────

def test_disease_db_has_entries():
    from ml.disease_db import AGRI_DATABASE
    keys_lower = [k.lower() for k in AGRI_DATABASE.keys()]
    assert "tomato" in keys_lower
    tomato_key = next(k for k in AGRI_DATABASE if k.lower() == "tomato")
    assert len(AGRI_DATABASE[tomato_key]) >= 3


def test_get_disease_info_returns_dict():
    from ml.disease_db import get_disease_info
    info = get_disease_info("Tomato", "early_blight")
    assert "severity"  in info
    assert "remedy"    in info
    assert "symptoms"  in info
