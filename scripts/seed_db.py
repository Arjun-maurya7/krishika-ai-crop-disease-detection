"""
scripts/seed_db.py  —  Krishika AI CSE494 MongoDB Project

Seeds all four MongoDB collections from CLASS_MAPPINGS and AGRI_DATABASE:
  - farmers       (empty — farmers self-register)
  - crops         (17 crops, with embedded growing_information)
  - diseases      (80+ disease documents, with economic_impact field)
  - detection_history (empty — filled by actual detections)

Run standalone:
    cd crop_desies_detection
    python -m scripts.seed_db

Or called at application startup via lifespan().
"""

import logging
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pymongo.database import Database

logger = logging.getLogger(__name__)

# ── Growing information for each crop (embedded sub-document) ─────────────────
GROWING_INFO: dict = {
    "Tomato":  {"season": "Kharif/Rabi", "soil_type": "Well-drained loamy", "water_needs": "Moderate", "harvest_days": "60-80"},
    "Apple":   {"season": "Temperate spring-summer", "soil_type": "Well-drained loam", "water_needs": "Moderate", "harvest_days": "140-180"},
    "Apricot": {"season": "Spring", "soil_type": "Sandy loam", "water_needs": "Low-moderate", "harvest_days": "100-120"},
    "Beans":   {"season": "Kharif/Rabi", "soil_type": "Loamy", "water_needs": "Moderate", "harvest_days": "50-65"},
    "Brinjal": {"season": "Kharif/Rabi/Summer", "soil_type": "Sandy loam to clay loam", "water_needs": "High", "harvest_days": "70-80"},
    "Cashew":  {"season": "Winter-Spring", "soil_type": "Sandy or laterite", "water_needs": "Low-moderate", "harvest_days": "60-70"},
    "cherry":  {"season": "Spring", "soil_type": "Well-drained loam", "water_needs": "Moderate", "harvest_days": "70-90"},
    "Corn":    {"season": "Kharif/Rabi", "soil_type": "Loamy to sandy loam", "water_needs": "Moderate", "harvest_days": "60-100"},
    "Cucumber":{"season": "Summer/Kharif", "soil_type": "Sandy loam", "water_needs": "High", "harvest_days": "45-65"},
    "Fig":     {"season": "Summer", "soil_type": "Deep loamy", "water_needs": "Moderate", "harvest_days": "90-120"},
    "Grape":   {"season": "Winter-Spring", "soil_type": "Sandy loam", "water_needs": "Moderate", "harvest_days": "150-180"},
    "Guava":   {"season": "Year-round (tropical)", "soil_type": "Various (adaptable)", "water_needs": "Moderate", "harvest_days": "120-180"},
    "Lychee":  {"season": "Summer", "soil_type": "Deep loamy", "water_needs": "High", "harvest_days": "70-100"},
    "Potato":  {"season": "Rabi", "soil_type": "Sandy loam", "water_needs": "Moderate", "harvest_days": "70-120"},
    "Radish":  {"season": "Winter/Rabi", "soil_type": "Sandy loam", "water_needs": "Low", "harvest_days": "25-60"},
    "Rice":    {"season": "Kharif", "soil_type": "Clay or clay loam", "water_needs": "Very high", "harvest_days": "120-150"},
    "Walnut":  {"season": "Temperate spring", "soil_type": "Deep loamy", "water_needs": "Moderate", "harvest_days": "150-200"},
}

# ── Economic impact descriptions for disease categories ───────────────────────
ECONOMIC_IMPACT_MAP: dict = {
    "healthy":  "No economic loss. Healthy plant yields are at full potential.",
    "medium": (
        "Moderate economic loss (10–30% yield reduction). Early intervention "
        "recommended to prevent progression to severe category."
    ),
    "high": (
        "Severe economic loss (30–70%+ yield reduction). Immediate treatment is "
        "essential. Untreated outbreaks can devastate entire fields and significantly "
        "impact farmer income and food security."
    ),
}


def _seed_crops(db: Database) -> None:
    """Upsert crop documents with embedded growing_information."""
    from ml.class_mappings import CLASS_MAPPINGS, CROP_DISPLAY_NAMES
    collection = db["crops"]
    for crop_key, disease_list in CLASS_MAPPINGS.items():
        doc = {
            "crop_id":           crop_key.lower(),
            "key":               crop_key,
            "name":              CROP_DISPLAY_NAMES.get(crop_key, crop_key),
            "description": (
                f"Supported crop with {len(disease_list)} disease/health classes. "
                f"Classified by a VGG19+SVM model trained on validated agricultural datasets."
            ),
            "supported_diseases": disease_list,
            "disease_count":      len(disease_list),
            "growing_information": GROWING_INFO.get(crop_key, {}),   # EMBEDDED sub-doc
        }
        collection.update_one(
            {"crop_id": doc["crop_id"]},
            {"$set": doc},
            upsert=True,
        )
    logger.info("Seeded %d crop documents.", len(CLASS_MAPPINGS))


def _seed_diseases(db: Database) -> None:
    """
    Upsert disease documents from AGRI_DATABASE.
    Adds economic_impact field based on severity.

    Academic note (CSE494):
      These are REFERENCED documents — diseases are stored separately from crops
      and joined at query time using $lookup aggregation.
      This avoids duplication and keeps the schema normalized.
    """
    from ml.disease_db import AGRI_DATABASE
    collection = db["diseases"]
    count      = 0
    for crop_key, diseases in AGRI_DATABASE.items():
        for disease_name, info in diseases.items():
            severity = info.get("severity", "medium")
            doc = {
                "disease_id":        f"{crop_key}_{disease_name}".replace(" ", "_").lower(),
                "crop_id":           crop_key.lower(),
                "crop_name":         crop_key,
                "disease_name":      disease_name,
                "symptoms":          info.get("symptoms", []),
                "causes":            info.get("cause", ""),
                "severity":          severity,
                "remedies":          info.get("remedy", ""),
                "preventive_measures": info.get("preventive_measures", []),
                "economic_impact":   ECONOMIC_IMPACT_MAP.get(
                    severity, ECONOMIC_IMPACT_MAP["medium"]
                ),
            }
            collection.update_one(
                {"disease_id": doc["disease_id"]},
                {"$set": doc},
                upsert=True,
            )
            count += 1
    logger.info("Seeded %d disease documents.", count)


def run_seed(db: Database) -> None:
    """Run all seed functions (safe to call multiple times — uses upsert)."""
    _seed_crops(db)
    _seed_diseases(db)
    logger.info("Database seeding complete.")


# ── Standalone execution ──────────────────────────────────────────────────────

if __name__ == "__main__":
    import logging
    from backend.config import get_settings
    from backend.database.connection import connect_db, close_db, get_db

    logging.basicConfig(level=logging.INFO)
    settings = get_settings()

    connect_db(settings.MONGO_URI, settings.MONGO_DB_NAME)
    db = get_db(settings.MONGO_DB_NAME)

    from backend.database.collections import ensure_collections_and_indexes
    ensure_collections_and_indexes(db)
    run_seed(db)
    close_db()
    print("[SUCCESS] Database seeded successfully.")
