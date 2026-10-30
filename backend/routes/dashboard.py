"""
backend/routes/dashboard.py  —  Krishika AI CSE494 MongoDB Project
Dashboard statistics powered by MongoDB aggregation pipelines.

GET /api/dashboard
GET /api/dashboard/global   (all-farmer admin view)
"""

import asyncio
import logging

from fastapi import APIRouter, Depends
from pymongo.database import Database

from backend.routes.deps import get_current_farmer, get_db
from backend.schemas.detection import (
    CropStatsItem,
    DashboardStats,
    DetectionListItem,
    DiseaseFrequencyItem,
    MonthlyTrendItem,
)
from backend.services.analytics_service import get_farmer_dashboard_stats, get_global_stats

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get(
    "",
    response_model=DashboardStats,
    summary="Farmer dashboard statistics (aggregation pipelines)",
)
async def get_dashboard(
    current_farmer: dict     = Depends(get_current_farmer),
    db:             Database = Depends(get_db),
):
    loop  = asyncio.get_event_loop()
    stats = await loop.run_in_executor(
        None,
        lambda: get_farmer_dashboard_stats(db, current_farmer["farmer_id"]),
    )
    return DashboardStats(
        total_scans     = stats["total_scans"],
        healthy_count   = stats["healthy_count"],
        diseased_count  = stats["diseased_count"],
        uncertain_count = stats["uncertain_count"],
        top_diseases    = [DiseaseFrequencyItem(**d) for d in stats["top_diseases"]],
        crop_stats      = [CropStatsItem(**c)        for c in stats["crop_stats"]],
        monthly_trend   = [MonthlyTrendItem(**m)     for m in stats["monthly_trend"]],
        recent_detections = [DetectionListItem(**r)  for r in stats["recent_detections"]],
    )


@router.get(
    "/global",
    summary="Global statistics across all farmers ($facet aggregation)",
)
async def get_global_dashboard(db: Database = Depends(get_db)):
    """
    Returns aggregated statistics across all farmers.
    Uses $facet aggregation to run multiple pipelines in one round-trip.
    """
    loop  = asyncio.get_event_loop()
    stats = await loop.run_in_executor(None, lambda: get_global_stats(db))
    return stats
