"""
backend/services/disease_service.py  —  Krishika AI CSE494 MongoDB Project

Synchronous PyMongo operations on the `diseases` and `crops` collections.
These functions are called from FastAPI routes via run_in_executor().

Academic note (CSE494):
  This service demonstrates:
  - Basic CRUD queries
  - $lookup aggregation (cross-collection join)
  - Sorting and projection
"""

import logging
from typing import Optional

from pymongo.database import Database

from backend.database.collections import CROPS_COLLECTION, DISEASES_COLLECTION, HISTORY_COLLECTION

logger = logging.getLogger(__name__)


# ── Disease queries ───────────────────────────────────────────────────────────

def get_disease_by_id(db: Database, disease_id: str) -> Optional[dict]:
    """Return a single disease document by its disease_id."""
    return db[DISEASES_COLLECTION].find_one({"disease_id": disease_id}, {"_id": 0})


def list_diseases_for_crop(db: Database, crop_name: str) -> list[dict]:
    """Return all disease documents for a given crop, sorted by name."""
    cursor = db[DISEASES_COLLECTION].find(
        {"crop_name": crop_name},
        {"_id": 0},
    ).sort("disease_name", 1)
    return list(cursor)


def search_diseases(
    db: Database,
    crop_name: Optional[str] = None,
    severity:  Optional[str] = None,
    keyword:   Optional[str] = None,
) -> list[dict]:
    """
    Search diseases with optional filters.

    Demonstrates:
    - Filtering: $regex text search on disease_name
    - Sorting
    - Projection
    """
    query: dict = {}
    if crop_name:
        query["crop_name"] = crop_name
    if severity:
        query["severity"] = severity
    if keyword:
        query["disease_name"] = {"$regex": keyword, "$options": "i"}

    cursor = db[DISEASES_COLLECTION].find(query, {"_id": 0}).sort("disease_name", 1)
    return list(cursor)


# ── Crop queries ──────────────────────────────────────────────────────────────

def get_all_crops(db: Database) -> list[dict]:
    """Return all crops sorted by name."""
    cursor = db[CROPS_COLLECTION].find({}, {"_id": 0}).sort("name", 1)
    return list(cursor)


def get_crop_by_id(db: Database, crop_id: str) -> Optional[dict]:
    """Return a crop document by crop_id."""
    return db[CROPS_COLLECTION].find_one({"crop_id": crop_id}, {"_id": 0})


# ── $lookup aggregation demo ──────────────────────────────────────────────────

def get_crop_with_disease_details(db: Database, crop_name: str) -> dict:
    """
    Fetch a crop with full embedded disease details using $lookup aggregation.

    Academic note (CSE494):
      This demonstrates the $lookup stage in MongoDB aggregation pipelines,
      which performs a JOIN between the `crops` and `diseases` collections.
      
      This is the "REFERENCING" pattern:
        - crops stores only the disease name list (reference)
        - diseases stores the full disease info (separate document)
        - $lookup joins them at query time
    """
    pipeline = [
        {
            "$match": {
                "$or": [
                    {"crop_id": crop_name.lower()},
                    {"key": crop_name},
                    {"name": {"$regex": f"^{crop_name}$", "$options": "i"}},
                ]
            }
        },
        {
            "$lookup": {
                "from":         DISEASES_COLLECTION,
                "localField":   "crop_id",      # crops.crop_id
                "foreignField": "crop_id",      # diseases.crop_id
                "as":           "disease_details",
            }
        },
        {
            "$project": {
                "_id":              0,
                "crop_id":          1,
                "name":             1,
                "description":      1,
                "supported_diseases": 1,
                "growing_information": 1,
                "disease_details":  {
                    "$map": {
                        "input": "$disease_details",
                        "as":    "d",
                        "in": {
                            "disease_name":        "$$d.disease_name",
                            "severity":            "$$d.severity",
                            "symptoms":            "$$d.symptoms",
                            "causes":              "$$d.causes",
                            "remedies":            "$$d.remedies",
                            "preventive_measures": "$$d.preventive_measures",
                            "economic_impact":     "$$d.economic_impact",
                        },
                    }
                },
            }
        },
    ]
    results = list(db[CROPS_COLLECTION].aggregate(pipeline))
    return results[0] if results else {}
