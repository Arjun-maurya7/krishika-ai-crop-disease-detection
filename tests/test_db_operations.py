"""
tests/test_db_operations.py  —  Krishika AI CSE494 MongoDB Project
Tests for MongoDB CRUD operations and aggregation pipelines.

Requires a running MongoDB instance (set MONGO_URI in environment or .env).
Uses a separate test database to avoid polluting production data.
"""

import os
import sys
import uuid
from datetime import datetime, timezone

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


TEST_DB_NAME = "krishika_cse494_test"


@pytest.fixture(scope="module")
def test_db():
    """Connect to a test database and clean up after tests."""
    from pymongo import MongoClient
    uri    = os.environ.get("MONGO_URI", "mongodb://localhost:27017")
    client = MongoClient(uri, serverSelectionTimeoutMS=3000)
    try:
        client.admin.command("ping")
    except Exception:
        pytest.skip("MongoDB not available — skipping DB tests.")
    
    db = client[TEST_DB_NAME]
    
    # Setup
    from backend.database.collections import ensure_collections_and_indexes
    ensure_collections_and_indexes(db)
    
    yield db
    
    # Teardown — drop test DB
    client.drop_database(TEST_DB_NAME)
    client.close()


# ── Farmers CRUD ──────────────────────────────────────────────────────────────

def test_insert_farmer(test_db):
    """Test inserting a farmer document with embedded location + stats."""
    doc = {
        "farmer_id":          str(uuid.uuid4()),
        "name":               "Ramesh Kumar",
        "email":              f"ramesh_{uuid.uuid4().hex[:6]}@test.com",
        "password_hash":      "hashed_password",
        "preferred_language": "en",
        "location":           {"state": "Punjab", "district": "Ludhiana"},
        "stats":              {"total_scans": 0, "last_scan_at": None},
        "created_at":         datetime.now(timezone.utc),
        "updated_at":         datetime.now(timezone.utc),
    }
    result = test_db["farmers"].insert_one(doc)
    assert result.inserted_id is not None
    
    # Verify retrieval
    found = test_db["farmers"].find_one({"farmer_id": doc["farmer_id"]}, {"_id": 0})
    assert found is not None
    assert found["name"] == "Ramesh Kumar"
    assert found["location"]["state"] == "Punjab"
    assert found["stats"]["total_scans"] == 0


def test_duplicate_email_rejected(test_db):
    """Unique email index must reject duplicates."""
    from pymongo.errors import DuplicateKeyError
    email = f"dup_{uuid.uuid4().hex[:6]}@test.com"
    base  = {
        "farmer_id": str(uuid.uuid4()), "name": "A", "email": email,
        "password_hash": "x", "preferred_language": "en",
        "location": {}, "stats": {"total_scans": 0, "last_scan_at": None},
        "created_at": datetime.now(timezone.utc), "updated_at": datetime.now(timezone.utc),
    }
    test_db["farmers"].insert_one(base.copy())
    with pytest.raises(DuplicateKeyError):
        base2        = base.copy()
        base2["farmer_id"] = str(uuid.uuid4())  # different ID, same email
        test_db["farmers"].insert_one(base2)


def test_update_farmer_stats(test_db):
    """$inc on embedded stats.total_scans."""
    farmer_id = str(uuid.uuid4())
    test_db["farmers"].insert_one({
        "farmer_id": farmer_id, "name": "B", "email": f"b_{farmer_id[:6]}@test.com",
        "password_hash": "x", "preferred_language": "en",
        "location": {}, "stats": {"total_scans": 0, "last_scan_at": None},
        "created_at": datetime.now(timezone.utc), "updated_at": datetime.now(timezone.utc),
    })
    test_db["farmers"].update_one(
        {"farmer_id": farmer_id},
        {"$inc": {"stats.total_scans": 1}},
    )
    updated = test_db["farmers"].find_one({"farmer_id": farmer_id}, {"_id": 0})
    assert updated["stats"]["total_scans"] == 1


# ── Crops CRUD ────────────────────────────────────────────────────────────────

def test_seed_crops(test_db):
    """Seeding crops populates crops collection."""
    from scripts.seed_db import _seed_crops
    _seed_crops(test_db)
    count = test_db["crops"].count_documents({})
    assert count == 17, f"Expected 17 crops, got {count}"


def test_crop_has_growing_information(test_db):
    """Crops should have embedded growing_information sub-document."""
    crop = test_db["crops"].find_one({"key": "Tomato"}, {"_id": 0})
    assert crop is not None
    assert "growing_information" in crop
    assert "season" in crop["growing_information"]


# ── Diseases CRUD ─────────────────────────────────────────────────────────────

def test_seed_diseases(test_db):
    """Seeding diseases populates diseases collection."""
    from scripts.seed_db import _seed_diseases
    _seed_diseases(test_db)
    count = test_db["diseases"].count_documents({})
    assert count > 50, f"Expected >50 diseases, got {count}"


def test_disease_has_economic_impact(test_db):
    """Each disease document should have economic_impact field."""
    disease = test_db["diseases"].find_one(
        {"crop_name": "Tomato", "disease_name": "early_blight"}, {"_id": 0}
    )
    assert disease is not None
    assert "economic_impact" in disease
    assert len(disease["economic_impact"]) > 10


# ── Detection History CRUD ────────────────────────────────────────────────────

def test_insert_detection(test_db):
    """Insert a detection_history record with embedded diagnosis."""
    farmer_id    = str(uuid.uuid4())
    detection_id = str(uuid.uuid4())
    doc = {
        "detection_id":      detection_id,
        "farmer_id":         farmer_id,
        "crop_name":         "Tomato",
        "predicted_disease": "early_blight",
        "confidence":        0.87,
        "is_uncertain":      False,
        "severity":          "medium",
        "prediction_status": "confident",
        "image_reference":   {"filename": "test.jpg", "path": "/uploads/test.jpg"},
        "diagnosis_details": {
            "cause":               "Alternaria solani fungus",
            "remedy":              "Apply mancozeb fungicide",
            "impact":              "Moderate yield loss",
            "symptoms":            ["Brown lesions with yellow halo"],
            "preventive_measures": ["Crop rotation", "Avoid overhead irrigation"],
        },
        "uncertainty_message": None,
        "detected_at":         datetime.now(timezone.utc),
    }
    test_db["detection_history"].insert_one(doc)
    found = test_db["detection_history"].find_one({"detection_id": detection_id}, {"_id": 0})
    assert found is not None
    assert found["diagnosis_details"]["cause"] == "Alternaria solani fungus"


def test_pagination(test_db):
    """list_detections should respect pagination."""
    farmer_id = str(uuid.uuid4())
    for i in range(5):
        test_db["detection_history"].insert_one({
            "detection_id":      str(uuid.uuid4()),
            "farmer_id":         farmer_id,
            "crop_name":         "Rice",
            "predicted_disease": "brown_spot",
            "confidence":        0.9,
            "is_uncertain":      False,
            "severity":          "medium",
            "prediction_status": "confident",
            "image_reference":   {},
            "diagnosis_details": {},
            "detected_at":       datetime.now(timezone.utc),
        })

    from pymongo import DESCENDING
    page1 = list(
        test_db["detection_history"]
        .find({"farmer_id": farmer_id}, {"_id": 0})
        .sort("detected_at", DESCENDING)
        .skip(0)
        .limit(3)
    )
    assert len(page1) == 3

    page2 = list(
        test_db["detection_history"]
        .find({"farmer_id": farmer_id}, {"_id": 0})
        .sort("detected_at", DESCENDING)
        .skip(3)
        .limit(3)
    )
    assert len(page2) == 2  # only 2 remaining


# ── Aggregation Pipelines ─────────────────────────────────────────────────────

def test_aggregation_totals(test_db):
    """$group aggregation should count records correctly."""
    farmer_id = str(uuid.uuid4())
    for i in range(3):
        test_db["detection_history"].insert_one({
            "detection_id":      str(uuid.uuid4()),
            "farmer_id":         farmer_id,
            "crop_name":         "Tomato",
            "predicted_disease": "healthy_leaf",
            "confidence":        0.95,
            "is_uncertain":      False,
            "severity":          "healthy",
            "prediction_status": "confident",
            "image_reference":   {},
            "diagnosis_details": {},
            "detected_at":       datetime.now(timezone.utc),
        })

    pipeline = [
        {"$match": {"farmer_id": farmer_id}},
        {
            "$group": {
                "_id":            None,
                "total_scans":    {"$sum": 1},
                "healthy_count":  {"$sum": {"$cond": [{"$eq": ["$severity", "healthy"]}, 1, 0]}},
            }
        },
    ]
    result = list(test_db["detection_history"].aggregate(pipeline))
    assert result[0]["total_scans"]   == 3
    assert result[0]["healthy_count"] == 3


def test_lookup_aggregation(test_db):
    """$lookup join between crops and diseases collections."""
    pipeline = [
        {"$match": {"key": "Tomato"}},
        {
            "$lookup": {
                "from":         "diseases",
                "localField":   "key",
                "foreignField": "crop_name",
                "as":           "disease_details",
            }
        },
        {"$limit": 1},
    ]
    result = list(test_db["crops"].aggregate(pipeline))
    assert len(result) == 1
    assert len(result[0].get("disease_details", [])) > 0
