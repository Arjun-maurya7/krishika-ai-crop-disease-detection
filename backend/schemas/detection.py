"""
backend/schemas/detection.py  —  Krishika AI CSE494 MongoDB Project
Pydantic models for disease detection responses, history, and dashboard.
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


# ── Embedded sub-schemas ──────────────────────────────────────────────────────

class DiagnosisDetail(BaseModel):
    """Embedded diagnosis information stored inside detection_history."""
    cause:               str       = ""
    remedy:              str       = ""
    impact:              str       = ""
    symptoms:            List[str] = []
    preventive_measures: List[str] = []


class ImageReference(BaseModel):
    """Embedded image file reference (filename + path stored; binary NOT in MongoDB)."""
    filename: Optional[str] = None
    path:     Optional[str] = None


# ── Detection Response ────────────────────────────────────────────────────────

class DetectionResponse(BaseModel):
    detection_id:        str
    farmer_id:           str
    crop_name:           str
    predicted_disease:   str
    confidence:          float
    is_uncertain:        bool
    severity:            str
    prediction_status:   str
    diagnosis:           DiagnosisDetail
    image_reference:     ImageReference
    uncertainty_message: Optional[str] = None
    detected_at:         datetime


# ── History / List ────────────────────────────────────────────────────────────

class DetectionListItem(BaseModel):
    detection_id:      str
    crop_name:         str
    predicted_disease: str
    confidence:        float
    severity:          str
    is_uncertain:      bool
    detected_at:       datetime


class DetectionListResponse(BaseModel):
    items:       List[DetectionListItem]
    total:       int
    page:        int
    page_size:   int
    total_pages: int


# ── Dashboard / Analytics ─────────────────────────────────────────────────────

class DiseaseFrequencyItem(BaseModel):
    disease: str
    count:   int


class CropStatsItem(BaseModel):
    crop:           str
    count:          int
    healthy_count:  int
    diseased_count: int


class MonthlyTrendItem(BaseModel):
    year:  int
    month: int
    count: int


class DashboardStats(BaseModel):
    total_scans:        int
    healthy_count:      int
    diseased_count:     int
    uncertain_count:    int
    top_diseases:       List[DiseaseFrequencyItem]
    crop_stats:         List[CropStatsItem]
    monthly_trend:      List[MonthlyTrendItem]
    recent_detections:  List[DetectionListItem]


# ── Disease Info ──────────────────────────────────────────────────────────────

class DiseaseInfoResponse(BaseModel):
    disease_id:          str
    crop_name:           str
    disease_name:        str
    symptoms:            List[str]
    causes:              str
    severity:            str
    remedies:            str
    preventive_measures: List[str]
    economic_impact:     str


class CropInfoResponse(BaseModel):
    crop_id:             str
    name:                str
    description:         str
    supported_diseases:  List[str]
    disease_count:       int
    growing_information: dict = {}
