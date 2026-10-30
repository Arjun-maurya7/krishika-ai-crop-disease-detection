"""
backend/routes/auth.py  —  Krishika AI CSE494 MongoDB Project

Farmer registration, login, and profile endpoints.

POST /api/auth/register
POST /api/auth/login
GET  /api/auth/me
PATCH /api/auth/me
"""

import asyncio
import logging
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from pymongo.database import Database
from pymongo.errors import DuplicateKeyError

from backend.routes.deps import get_current_farmer, get_db
from backend.schemas.farmer import (
    FarmerLoginRequest,
    FarmerRegisterRequest,
    FarmerResponse,
    FarmerStatsResponse,
    FarmerUpdateRequest,
    LocationResponse,
    TokenResponse,
)
from backend.services.auth_service import create_access_token, hash_password, verify_password

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/auth", tags=["Authentication"])


def _to_farmer_response(doc: dict) -> FarmerResponse:
    stats_raw = doc.get("stats", {})
    return FarmerResponse(
        farmer_id          = doc["farmer_id"],
        name               = doc["name"],
        email              = doc["email"],
        preferred_language = doc.get("preferred_language", "en"),
        location           = LocationResponse(
            state    = doc.get("location", {}).get("state"),
            district = doc.get("location", {}).get("district"),
        ),
        stats = FarmerStatsResponse(
            total_scans  = stats_raw.get("total_scans", 0),
            last_scan_at = stats_raw.get("last_scan_at"),
        ),
        created_at = doc["created_at"],
    )


def _create_farmer_doc(
    name:               str,
    email:              str,
    password_hash:      str,
    preferred_language: str = "en",
    location_state:     str | None = None,
    location_district:  str | None = None,
) -> dict:
    now = datetime.now(timezone.utc)
    return {
        "farmer_id":          str(uuid.uuid4()),
        "name":               name,
        "email":              email.lower(),
        "password_hash":      password_hash,
        "preferred_language": preferred_language,
        "location": {
            "state":    location_state,
            "district": location_district,
        },
        "stats": {          # EMBEDDED sub-document
            "total_scans": 0,
            "last_scan_at": None,
        },
        "created_at": now,
        "updated_at": now,
    }


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new farmer account",
)
async def register(
    body: FarmerRegisterRequest,
    db:   Database = Depends(get_db),
):
    password_hash = hash_password(body.password)
    doc           = _create_farmer_doc(
        name               = body.name,
        email              = body.email,
        password_hash      = password_hash,
        preferred_language = body.preferred_language,
        location_state     = body.location_state,
        location_district  = body.location_district,
    )

    loop = asyncio.get_event_loop()
    try:
        await loop.run_in_executor(None, lambda: db["farmers"].insert_one(doc))
    except DuplicateKeyError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists.",
        )

    doc.pop("_id", None)
    token = create_access_token({"sub": doc["farmer_id"]})
    logger.info("New farmer registered: %s", doc["email"])
    return TokenResponse(access_token=token, farmer=_to_farmer_response(doc))


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login and receive a JWT access token",
)
async def login(
    body: FarmerLoginRequest,
    db:   Database = Depends(get_db),
):
    loop   = asyncio.get_event_loop()
    farmer = await loop.run_in_executor(
        None,
        lambda: db["farmers"].find_one({"email": body.email.lower()}, {"_id": 0}),
    )
    if farmer is None or not verify_password(body.password, farmer["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
        )

    token = create_access_token({"sub": farmer["farmer_id"]})
    logger.info("Farmer logged in: %s", farmer["email"])
    return TokenResponse(access_token=token, farmer=_to_farmer_response(farmer))


@router.get(
    "/me",
    response_model=FarmerResponse,
    summary="Get the authenticated farmer's profile",
)
async def get_me(current_farmer: dict = Depends(get_current_farmer)):
    return _to_farmer_response(current_farmer)


@router.patch(
    "/me",
    response_model=FarmerResponse,
    summary="Update the authenticated farmer's profile",
)
async def update_me(
    body:           FarmerUpdateRequest,
    current_farmer: dict     = Depends(get_current_farmer),
    db:             Database = Depends(get_db),
):
    updates: dict = {}
    if body.name               is not None: updates["name"]               = body.name
    if body.preferred_language is not None: updates["preferred_language"] = body.preferred_language
    if body.location_state     is not None: updates["location.state"]     = body.location_state
    if body.location_district  is not None: updates["location.district"]  = body.location_district

    if not updates:
        raise HTTPException(status_code=400, detail="No updates provided.")

    updates["updated_at"] = datetime.now(timezone.utc)
    loop    = asyncio.get_event_loop()
    updated = await loop.run_in_executor(
        None,
        lambda: db["farmers"].find_one_and_update(
            {"farmer_id": current_farmer["farmer_id"]},
            {"$set": updates},
            return_document=True,
            projection={"_id": 0, "password_hash": 0},
        ),
    )
    if updated is None:
        raise HTTPException(status_code=404, detail="Farmer not found.")
    return _to_farmer_response(updated)
