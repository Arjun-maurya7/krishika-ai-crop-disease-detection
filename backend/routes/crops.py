"""
backend/routes/crops.py  —  Krishika AI CSE494 MongoDB Project
Crop and disease information endpoints.

GET /api/crops
GET /api/crops/{crop_id}
GET /api/crops/{crop_id}/diseases   ($lookup join)
GET /api/diseases
GET /api/diseases/{disease_id}
"""

import asyncio
import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pymongo.database import Database

from backend.routes.deps import get_db
from backend.schemas.detection import CropInfoResponse, DiseaseInfoResponse
from backend.services.disease_service import (
    get_all_crops,
    get_crop_by_id,
    get_crop_with_disease_details,
    get_disease_by_id,
    list_diseases_for_crop,
    search_diseases,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["Crops & Diseases"])


@router.get("/crops", summary="List all supported crops")
async def list_crops(db: Database = Depends(get_db)):
    loop  = asyncio.get_event_loop()
    crops = await loop.run_in_executor(None, lambda: get_all_crops(db))
    return {"crops": crops, "total": len(crops)}


@router.get("/crops/{crop_id}", summary="Get crop details")
async def get_crop(crop_id: str, db: Database = Depends(get_db)):
    loop = asyncio.get_event_loop()
    crop = await loop.run_in_executor(None, lambda: get_crop_by_id(db, crop_id))
    if crop is None:
        raise HTTPException(status_code=404, detail=f"Crop '{crop_id}' not found.")
    return crop


@router.get(
    "/crops/{crop_name}/diseases",
    summary="Get crop with full disease details ($lookup join)",
)
async def get_crop_diseases(crop_name: str, db: Database = Depends(get_db)):
    """
    Returns a crop document joined with all its disease records.
    Demonstrates MongoDB $lookup aggregation (cross-collection join).
    """
    loop   = asyncio.get_event_loop()
    result = await loop.run_in_executor(
        None, lambda: get_crop_with_disease_details(db, crop_name)
    )
    if not result:
        raise HTTPException(status_code=404, detail=f"Crop '{crop_name}' not found.")
    return result


@router.get("/diseases", summary="Search / list diseases")
async def list_diseases(
    crop:     Optional[str] = Query(default=None, description="Filter by crop name"),
    severity: Optional[str] = Query(default=None, description="Filter by severity"),
    keyword:  Optional[str] = Query(default=None, description="Search disease name"),
    db:       Database = Depends(get_db),
):
    loop    = asyncio.get_event_loop()
    results = await loop.run_in_executor(
        None, lambda: search_diseases(db, crop, severity, keyword)
    )
    return {"diseases": results, "total": len(results)}


@router.get("/diseases/{disease_id}", summary="Get a single disease record")
async def get_disease(disease_id: str, db: Database = Depends(get_db)):
    loop    = asyncio.get_event_loop()
    disease = await loop.run_in_executor(None, lambda: get_disease_by_id(db, disease_id))
    if disease is None:
        raise HTTPException(status_code=404, detail=f"Disease '{disease_id}' not found.")
    return disease
