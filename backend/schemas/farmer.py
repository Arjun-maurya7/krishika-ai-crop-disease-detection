"""
backend/schemas/farmer.py  —  Krishika AI CSE494 MongoDB Project
Pydantic models for farmer authentication and profile management.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator


# ── Request Models ────────────────────────────────────────────────────────────

class FarmerRegisterRequest(BaseModel):
    name:               str      = Field(..., min_length=2, max_length=100, json_schema_extra={"example": "Ramesh Kumar"})
    email:              EmailStr = Field(..., json_schema_extra={"example": "ramesh@example.com"})
    password:           str      = Field(..., min_length=8, max_length=128, json_schema_extra={"example": "securepass123"})
    preferred_language: str      = Field(default="en", pattern="^(en|hi|pa)$")
    location_state:     Optional[str] = Field(default=None, max_length=100)
    location_district:  Optional[str] = Field(default=None, max_length=100)

    @field_validator("name")
    @classmethod
    def name_must_not_be_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Name must not be blank.")
        return v.strip()


class FarmerLoginRequest(BaseModel):
    email:    EmailStr = Field(..., json_schema_extra={"example": "ramesh@example.com"})
    password: str      = Field(..., min_length=1)


class FarmerUpdateRequest(BaseModel):
    name:               Optional[str] = Field(default=None, min_length=2, max_length=100)
    preferred_language: Optional[str] = Field(default=None, pattern="^(en|hi|pa)$")
    location_state:     Optional[str] = Field(default=None, max_length=100)
    location_district:  Optional[str] = Field(default=None, max_length=100)


# ── Response Models ───────────────────────────────────────────────────────────

class LocationResponse(BaseModel):
    state:    Optional[str] = None
    district: Optional[str] = None


class FarmerStatsResponse(BaseModel):
    total_scans: int             = 0
    last_scan_at: Optional[datetime] = None


class FarmerResponse(BaseModel):
    farmer_id:          str
    name:               str
    email:              str
    preferred_language: str
    location:           LocationResponse
    stats:              FarmerStatsResponse = FarmerStatsResponse()
    created_at:         datetime


class TokenResponse(BaseModel):
    access_token: str
    token_type:   str = "bearer"
    farmer:       FarmerResponse
