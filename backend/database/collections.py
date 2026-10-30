"""
backend/database/collections.py  —  Krishika AI CSE494 MongoDB Project

Collection name constants, index specifications, and MongoDB $jsonSchema
validators for each collection.

Academic note (CSE494):
  This module demonstrates:
  - Collection-level schema validation using MongoDB's $jsonSchema
  - Index design (unique, compound, single-field)
  - Embedded vs referenced document design decisions

Collections:
  farmers          — farmer accounts (embedded location + stats)
  crops            — crop reference data (embedded growing_information)
  diseases         — disease reference data (referenced by detection_history)
  detection_history — per-scan records (embedded diagnosis + image ref)
"""

import logging
from pymongo import ASCENDING, DESCENDING, IndexModel
from pymongo.database import Database

logger = logging.getLogger(__name__)

# ── Collection Name Constants ─────────────────────────────────────────────────
FARMERS_COLLECTION   = "farmers"
CROPS_COLLECTION     = "crops"
DISEASES_COLLECTION  = "diseases"
HISTORY_COLLECTION   = "detection_history"


# ── $jsonSchema Validators ────────────────────────────────────────────────────

FARMERS_SCHEMA = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["farmer_id", "name", "email", "password_hash", "created_at"],
        "properties": {
            "farmer_id":          {"bsonType": "string",  "description": "UUID string, required"},
            "name":               {"bsonType": "string",  "minLength": 2, "maxLength": 100},
            "email":              {"bsonType": "string",  "pattern": "^[^@]+@[^@]+\\.[^@]+$"},
            "password_hash":      {"bsonType": "string"},
            "preferred_language": {"bsonType": "string",  "enum": ["en", "hi", "pa"]},
            "location": {
                "bsonType": "object",
                "properties": {
                    "state":    {"bsonType": ["string", "null"]},
                    "district": {"bsonType": ["string", "null"]},
                },
            },
            "stats": {
                "bsonType": "object",
                "properties": {
                    "total_scans": {"bsonType": "int"},
                    "last_scan_at": {"bsonType": ["date", "null"]},
                },
            },
            "created_at": {"bsonType": "date"},
            "updated_at": {"bsonType": "date"},
        },
    }
}

HISTORY_SCHEMA = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": [
            "detection_id", "farmer_id", "crop_name",
            "predicted_disease", "confidence", "severity", "detected_at",
        ],
        "properties": {
            "detection_id":      {"bsonType": "string"},
            "farmer_id":         {"bsonType": "string"},
            "crop_name":         {"bsonType": "string"},
            "predicted_disease": {"bsonType": "string"},
            "confidence":        {"bsonType": "double",  "minimum": 0.0, "maximum": 1.0},
            "severity":          {"bsonType": "string",  "enum": ["healthy", "medium", "high"]},
            "prediction_status": {"bsonType": "string",  "enum": ["confident", "uncertain", "low_accuracy_crop"]},
            "detected_at":       {"bsonType": "date"},
        },
    }
}


# ── Collection + Index Initialisation ────────────────────────────────────────

def ensure_collections_and_indexes(db: Database) -> None:
    """
    Create all collections (with $jsonSchema validators) and their indexes.
    Safe to call multiple times — uses upsert / create_if_not_exists patterns.

    Academic note: MongoDB schema validation is applied at the collection level
    with validationAction="warn" so that existing data is not rejected.
    """
    existing = db.list_collection_names()

    # ── farmers ───────────────────────────────────────────────────────────────
    if FARMERS_COLLECTION not in existing:
        db.create_collection(
            FARMERS_COLLECTION,
            validator=FARMERS_SCHEMA,
            validationAction="warn",   # warn mode: log violations, don't reject
        )
        logger.info("Created 'farmers' collection with $jsonSchema validator.")

    db[FARMERS_COLLECTION].create_indexes([
        IndexModel([("email",     ASCENDING)], unique=True, name="email_unique"),
        IndexModel([("farmer_id", ASCENDING)], unique=True, name="farmer_id_unique"),
    ])
    logger.info("Farmers indexes ensured.")

    # ── crops ─────────────────────────────────────────────────────────────────
    if CROPS_COLLECTION not in existing:
        db.create_collection(CROPS_COLLECTION)
        logger.info("Created 'crops' collection.")

    db[CROPS_COLLECTION].create_indexes([
        IndexModel([("crop_id", ASCENDING)], unique=True, name="crop_id_unique"),
        IndexModel([("name",    ASCENDING)], name="crop_name_idx"),
    ])
    logger.info("Crops indexes ensured.")

    # ── diseases ──────────────────────────────────────────────────────────────
    if DISEASES_COLLECTION not in existing:
        db.create_collection(DISEASES_COLLECTION)
        logger.info("Created 'diseases' collection.")

    db[DISEASES_COLLECTION].create_indexes([
        IndexModel([("disease_id",  ASCENDING)], unique=True, name="disease_id_unique"),
        IndexModel([("crop_name",   ASCENDING)], name="diseases_crop_idx"),
        IndexModel([("severity",    ASCENDING)], name="diseases_severity_idx"),
        IndexModel([("disease_name", ASCENDING)], name="diseases_name_idx"),
    ])
    logger.info("Diseases indexes ensured.")

    # ── detection_history ─────────────────────────────────────────────────────
    if HISTORY_COLLECTION not in existing:
        db.create_collection(
            HISTORY_COLLECTION,
            validator=HISTORY_SCHEMA,
            validationAction="warn",
        )
        logger.info("Created 'detection_history' collection with $jsonSchema validator.")

    db[HISTORY_COLLECTION].create_indexes([
        IndexModel([("detection_id", ASCENDING)], unique=True, name="detection_id_unique"),
        IndexModel([("farmer_id",    ASCENDING)], name="farmer_id_idx"),
        IndexModel([("crop_name",    ASCENDING)], name="crop_name_idx"),
        IndexModel([("severity",     ASCENDING)], name="severity_idx"),
        # Compound index: farmer's history sorted by time (most common query)
        IndexModel(
            [("farmer_id", ASCENDING), ("detected_at", DESCENDING)],
            name="farmer_time_compound_idx",
        ),
        # Compound index: filter by crop + farmer
        IndexModel(
            [("farmer_id", ASCENDING), ("crop_name", ASCENDING)],
            name="farmer_crop_compound_idx",
        ),
    ])
    logger.info("Detection history indexes ensured.")

    logger.info("All MongoDB collections and indexes are ready.")
