"""
backend/routes/history.py  —  Krishika AI CSE494 MongoDB Project

Detection history endpoints for authenticated farmers.

GET    /api/history
GET    /api/history/{detection_id}
DELETE /api/history/{detection_id}
"""

import asyncio
import logging
import math
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pymongo import DESCENDING
from pymongo.database import Database

from backend.routes.deps import get_current_farmer, get_db
from backend.schemas.detection import (
    DetectionListItem,
    DetectionListResponse,
    DetectionResponse,
    DiagnosisDetail,
    ImageReference,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/history", tags=["Detection History"])

COLLECTION = "detection_history"


@router.get(
    "",
    response_model=DetectionListResponse,
    summary="List all detection records (paginated)",
)
async def list_history(
    page:       int            = Query(default=1,  ge=1,  description="Page number"),
    page_size:  int            = Query(default=10, ge=1, le=50, description="Items per page"),
    crop:       Optional[str]  = Query(default=None, description="Filter by crop name"),
    severity:   Optional[str]  = Query(default=None, pattern="^(healthy|medium|high)$"),
    date_from:  Optional[datetime] = Query(default=None, description="ISO datetime lower bound"),
    date_to:    Optional[datetime] = Query(default=None, description="ISO datetime upper bound"),
    current_farmer: dict     = Depends(get_current_farmer),
    db:             Database = Depends(get_db),
):
    query: dict = {"farmer_id": current_farmer["farmer_id"]}
    if crop:      query["crop_name"] = crop
    if severity:  query["severity"]  = severity
    if date_from or date_to:
        dq: dict = {}
        if date_from: dq["$gte"] = date_from
        if date_to:   dq["$lte"] = date_to
        query["detected_at"] = dq

    skip = (page - 1) * page_size

    loop = asyncio.get_event_loop()

    def _query():
        total = db[COLLECTION].count_documents(query)
        items = list(
            db[COLLECTION]
            .find(query, {"_id": 0})
            .sort("detected_at", DESCENDING)
            .skip(skip)
            .limit(page_size)
        )
        return items, total

    items, total = await loop.run_in_executor(None, _query)

    list_items = [
        DetectionListItem(
            detection_id      = d["detection_id"],
            crop_name         = d["crop_name"],
            predicted_disease = d["predicted_disease"],
            confidence        = d["confidence"],
            severity          = d["severity"],
            is_uncertain      = d.get("is_uncertain", False),
            detected_at       = d["detected_at"],
        )
        for d in items
    ]

    total_pages = math.ceil(total / page_size) if total > 0 else 1
    return DetectionListResponse(
        items=list_items, total=total, page=page,
        page_size=page_size, total_pages=total_pages,
    )


@router.get(
    "/{detection_id}",
    response_model=DetectionResponse,
    summary="Get a single detection record",
)
async def get_detection(
    detection_id:   str,
    current_farmer: dict     = Depends(get_current_farmer),
    db:             Database = Depends(get_db),
):
    loop = asyncio.get_event_loop()
    doc  = await loop.run_in_executor(
        None,
        lambda: db[COLLECTION].find_one(
            {"detection_id": detection_id, "farmer_id": current_farmer["farmer_id"]},
            {"_id": 0},
        ),
    )
    if doc is None:
        raise HTTPException(status_code=404, detail="Detection record not found.")

    return DetectionResponse(
        detection_id        = doc["detection_id"],
        farmer_id           = doc["farmer_id"],
        crop_name           = doc["crop_name"],
        predicted_disease   = doc["predicted_disease"],
        confidence          = doc["confidence"],
        is_uncertain        = doc.get("is_uncertain", False),
        severity            = doc["severity"],
        prediction_status   = doc.get("prediction_status", "confident"),
        diagnosis           = DiagnosisDetail(**doc.get("diagnosis_details", {})),
        image_reference     = ImageReference(**doc.get("image_reference", {})),
        uncertainty_message = doc.get("uncertainty_message"),
        detected_at         = doc["detected_at"],
    )


@router.delete(
    "/{detection_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a detection record",
)
async def delete_detection(
    detection_id:   str,
    current_farmer: dict     = Depends(get_current_farmer),
    db:             Database = Depends(get_db),
):
    loop   = asyncio.get_event_loop()
    result = await loop.run_in_executor(
        None,
        lambda: db[COLLECTION].delete_one(
            {"detection_id": detection_id, "farmer_id": current_farmer["farmer_id"]}
        ),
    )
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=404,
            detail="Detection record not found or you are not authorised to delete it.",
        )
    # Decrement farmer stats
    await loop.run_in_executor(
        None,
        lambda: db["farmers"].update_one(
            {"farmer_id": current_farmer["farmer_id"]},
            {"$inc": {"stats.total_scans": -1}},
        ),
    )
