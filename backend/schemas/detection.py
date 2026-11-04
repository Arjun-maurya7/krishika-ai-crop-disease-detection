"""
backend/schemas/detection.py  —  Krishika AI CSE494 MongoDB Project
Pydantic models for disease detection responses, history, and dashboard.
"""

from datetime import datetime
from typing import Any, List, Optional

from pydantic import BaseModel, Field, model_validator


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
    remedy:            Optional[str] = None
    diagnosis:         Optional[DiagnosisDetail] = None
    image_url:         Optional[str] = None
    id:                Optional[str] = None
    crop:              Optional[str] = None
    disease:           Optional[str] = None
    created_at:        Optional[datetime] = None

    @model_validator(mode="before")
    @classmethod
    def pre_populate(cls, values: Any) -> Any:
        if isinstance(values, dict):
            if not values.get("id") and values.get("detection_id"):
                values["id"] = values["detection_id"]
            if not values.get("crop") and values.get("crop_name"):
                values["crop"] = values["crop_name"]
            if not values.get("disease") and values.get("predicted_disease"):
                values["disease"] = values["predicted_disease"]
            if not values.get("created_at") and values.get("detected_at"):
                values["created_at"] = values["detected_at"]
            diag = values.get("diagnosis_details")
            if not values.get("remedy") and isinstance(diag, dict):
                values["remedy"] = diag.get("remedy")
            if not values.get("diagnosis") and isinstance(diag, dict):
                values["diagnosis"] = diag
            img_ref = values.get("image_reference")
            if not values.get("image_url") and isinstance(img_ref, dict):
                fn = img_ref.get("filename")
                did = values.get("detection_id")
                if fn and did:
                    values["image_url"] = f"/uploads/{did}/{fn}"
        return values

    @model_validator(mode="after")
    def populate_aliases(self):
        if not self.id:
            self.id = self.detection_id
        if not self.crop:
            self.crop = self.crop_name
        if not self.disease:
            self.disease = self.predicted_disease
        if not self.created_at:
            self.created_at = self.detected_at
        if not self.remedy and self.diagnosis:
            self.remedy = self.diagnosis.remedy
        return self


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
