"""
backend/services/analytics_service.py  —  Krishika AI CSE494 MongoDB Project

MongoDB aggregation pipelines for the analytics dashboard.

Academic note (CSE494):
  This module demonstrates multiple complex aggregation pipelines:
  1. $match + $group + $project  → summary totals
  2. $group + $sort + $limit     → top diseases
  3. $group by compound id       → monthly trend
  4. $lookup                     → join detection with disease records
  5. $facet                      → multiple aggregations in one query
"""

import logging
from datetime import datetime, timezone, timedelta

from pymongo import ASCENDING, DESCENDING
from pymongo.database import Database

from backend.database.collections import DISEASES_COLLECTION, HISTORY_COLLECTION

logger = logging.getLogger(__name__)


def get_farmer_dashboard_stats(db: Database, farmer_id: str) -> dict:
    """
    Run MongoDB aggregation pipelines to produce per-farmer dashboard stats.

    Demonstrates $match, $group, $project, $sort, $limit, $cond, $subtract.

    Returns dict with:
        total_scans, healthy_count, diseased_count, uncertain_count,
        top_diseases, crop_stats, monthly_trend, recent_detections
    """

    # ── 1. Totals ──────────────────────────────────────────────────────────────
    totals_pipeline = [
        {"$match": {"farmer_id": farmer_id}},
        {
            "$group": {
                "_id": None,
                "total_scans":    {"$sum": 1},
                "healthy_count":  {"$sum": {"$cond": [{"$eq": ["$severity", "healthy"]}, 1, 0]}},
                "uncertain_count":{"$sum": {"$cond": [{"$eq": ["$prediction_status", "uncertain"]}, 1, 0]}},
            }
        },
    ]
    totals_result  = list(db[HISTORY_COLLECTION].aggregate(totals_pipeline))
    totals         = totals_result[0] if totals_result else {}
    total_scans    = totals.get("total_scans",    0)
    healthy_count  = totals.get("healthy_count",  0)
    uncertain_count= totals.get("uncertain_count", 0)
    diseased_count = total_scans - healthy_count

    # ── 2. Top 5 diseases (excluding healthy) ─────────────────────────────────
    top_diseases_pipeline = [
        {"$match": {"farmer_id": farmer_id, "severity": {"$ne": "healthy"}}},
        {"$group": {"_id": "$predicted_disease", "count": {"$sum": 1}}},
        {"$sort":  {"count": DESCENDING}},
        {"$limit": 5},
        {"$project": {"_id": 0, "disease": "$_id", "count": 1}},
    ]
    top_diseases = list(db[HISTORY_COLLECTION].aggregate(top_diseases_pipeline))

    # ── 3. Crop-wise stats ─────────────────────────────────────────────────────
    crop_pipeline = [
        {"$match": {"farmer_id": farmer_id}},
        {
            "$group": {
                "_id":           "$crop_name",
                "count":         {"$sum": 1},
                "healthy_count": {"$sum": {"$cond": [{"$eq": ["$severity", "healthy"]}, 1, 0]}},
            }
        },
        {"$sort": {"count": DESCENDING}},
        {
            "$project": {
                "_id":           0,
                "crop":          "$_id",
                "count":         1,
                "healthy_count": 1,
                "diseased_count": {"$subtract": ["$count", "$healthy_count"]},
            }
        },
    ]
    crop_stats = list(db[HISTORY_COLLECTION].aggregate(crop_pipeline))

    # ── 4. Monthly detection trend (last 12 months) ────────────────────────────
    cutoff = datetime.now(timezone.utc) - timedelta(days=365)
    monthly_pipeline = [
        {"$match": {"farmer_id": farmer_id, "detected_at": {"$gte": cutoff}}},
        {
            "$group": {
                "_id": {
                    "year":  {"$year":  "$detected_at"},
                    "month": {"$month": "$detected_at"},
                },
                "count": {"$sum": 1},
            }
        },
        {"$sort": {"_id.year": ASCENDING, "_id.month": ASCENDING}},
        {
            "$project": {
                "_id":   0,
                "year":  "$_id.year",
                "month": "$_id.month",
                "count": 1,
            }
        },
    ]
    monthly_trend = list(db[HISTORY_COLLECTION].aggregate(monthly_pipeline))

    # ── 5. Recent 5 detections ────────────────────────────────────────────────
    recent_detections = list(
        db[HISTORY_COLLECTION]
        .find(
            {"farmer_id": farmer_id},
            {
                "_id": 0,
                "detection_id": 1, "crop_name": 1, "predicted_disease": 1,
                "confidence": 1, "severity": 1, "is_uncertain": 1, "detected_at": 1,
            },
        )
        .sort("detected_at", DESCENDING)
        .limit(5)
    )

    return {
        "total_scans":       total_scans,
        "healthy_count":     healthy_count,
        "diseased_count":    diseased_count,
        "uncertain_count":   uncertain_count,
        "top_diseases":      top_diseases,
        "crop_stats":        crop_stats,
        "monthly_trend":     monthly_trend,
        "recent_detections": recent_detections,
    }


def get_global_stats(db: Database) -> dict:
    """
    Global aggregation across ALL farmers — demonstrates $facet for multiple
    aggregations in a single round-trip.

    Academic note: $facet allows running multiple independent sub-pipelines
    in a single aggregation command, which is more efficient than separate queries.
    """
    pipeline = [
        {
            "$facet": {
                "totals": [
                    {
                        "$group": {
                            "_id": None,
                            "total_scans":   {"$sum": 1},
                            "healthy_count": {"$sum": {"$cond": [{"$eq": ["$severity", "healthy"]}, 1, 0]}},
                            "unique_farmers": {"$addToSet": "$farmer_id"},
                        }
                    },
                    {
                        "$project": {
                            "_id":            0,
                            "total_scans":    1,
                            "healthy_count":  1,
                            "total_farmers":  {"$size": "$unique_farmers"},
                        }
                    },
                ],
                "top_diseases": [
                    {"$match": {"severity": {"$ne": "healthy"}}},
                    {"$group": {"_id": "$predicted_disease", "count": {"$sum": 1}}},
                    {"$sort":  {"count": DESCENDING}},
                    {"$limit": 10},
                    {"$project": {"_id": 0, "disease": "$_id", "count": 1}},
                ],
                "crop_distribution": [
                    {"$group": {"_id": "$crop_name", "count": {"$sum": 1}}},
                    {"$sort":  {"count": DESCENDING}},
                    {"$project": {"_id": 0, "crop": "$_id", "count": 1}},
                ],
                "severity_distribution": [
                    {"$group": {"_id": "$severity", "count": {"$sum": 1}}},
                    {"$project": {"_id": 0, "severity": "$_id", "count": 1}},
                ],
            }
        }
    ]

    result = list(db[HISTORY_COLLECTION].aggregate(pipeline))
    if not result:
        return {}

    data     = result[0]
    totals   = data.get("totals", [{}])[0] if data.get("totals") else {}
    return {
        "total_scans":          totals.get("total_scans", 0),
        "healthy_count":        totals.get("healthy_count", 0),
        "total_farmers":        totals.get("total_farmers", 0),
        "top_diseases":         data.get("top_diseases", []),
        "crop_distribution":    data.get("crop_distribution", []),
        "severity_distribution": data.get("severity_distribution", []),
    }


def get_detection_with_disease_info(db: Database, detection_id: str, farmer_id: str) -> dict:
    """
    Fetch a single detection record joined with disease reference data via $lookup.

    Academic note: Demonstrates combining REFERENCING (detection → disease name)
    with $lookup to enrich the result without duplicating the disease data
    inside every detection record.
    """
    pipeline = [
        {"$match": {"detection_id": detection_id, "farmer_id": farmer_id}},
        {
            "$lookup": {
                "from": DISEASES_COLLECTION,
                "let":  {"crop": "$crop_name", "disease": "$predicted_disease"},
                "pipeline": [
                    {
                        "$match": {
                            "$expr": {
                                "$and": [
                                    {"$eq": ["$crop_name",    "$$crop"]},
                                    {"$eq": ["$disease_name", "$$disease"]},
                                ]
                            }
                        }
                    },
                    {"$project": {"_id": 0}},
                ],
                "as": "disease_ref",
            }
        },
        {"$project": {"_id": 0}},
    ]
    results = list(db[HISTORY_COLLECTION].aggregate(pipeline))
    return results[0] if results else {}
