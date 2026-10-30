"""
backend/routes/detection.py  —  Krishika AI CSE494 MongoDB Project

Disease detection endpoint — receives image + crop, runs ML, saves to MongoDB.

POST /api/detect
"""

import asyncio
import logging
import uuid
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from pymongo.database import Database

from backend.config import get_settings
from backend.routes.deps import get_current_farmer, get_db
from backend.schemas.detection import DetectionResponse, DiagnosisDetail, ImageReference
from backend.services.prediction_service import run_prediction
from ml.class_mappings import CLASS_MAPPINGS

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["Disease Detection"])


def _validate_image(file: UploadFile) -> None:
    settings = get_settings()
    if file.content_type not in settings.ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Unsupported image type: {file.content_type}. "
                f"Accepted: {', '.join(settings.ALLOWED_IMAGE_TYPES)}"
            ),
        )


async def _save_image(contents: bytes, detection_id: str, original_filename: str) -> tuple[str, str]:
    """Save image bytes to disk. Returns (filename, full_path)."""
    settings   = get_settings()
    upload_dir = Path(settings.UPLOAD_DIR) / detection_id
    upload_dir.mkdir(parents=True, exist_ok=True)

    max_bytes = int(settings.MAX_IMAGE_SIZE_MB * 1024 * 1024)
    if len(contents) > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Image too large. Maximum size is {settings.MAX_IMAGE_SIZE_MB} MB.",
        )

    ext      = Path(original_filename).suffix or ".jpg"
    filename = f"{detection_id}{ext}"
    filepath = upload_dir / filename
    loop     = asyncio.get_event_loop()
    await loop.run_in_executor(None, lambda: filepath.write_bytes(contents))
    return filename, str(filepath)


def _decode_image(contents: bytes):
    """Decode image bytes → numpy array (BGR)."""
    import cv2
    import numpy as np
    arr = np.frombuffer(contents, dtype=np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if img is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not decode image. Please upload a valid JPEG or PNG.",
        )
    return img


def _determine_prediction_status(is_uncertain: bool, crop: str) -> str:
    from ml.class_mappings import LOW_ACCURACY_CROPS
    if crop in LOW_ACCURACY_CROPS:
        return "low_accuracy_crop"
    if is_uncertain:
        return "uncertain"
    return "confident"


@router.post(
    "/detect",
    response_model=DetectionResponse,
    status_code=status.HTTP_200_OK,
    summary="Detect disease in a crop leaf image",
)
async def detect_disease(
    crop:           str        = Form(..., description="Crop key e.g. 'Tomato'"),
    image:          UploadFile = File(..., description="Leaf image (JPEG/PNG, max 10 MB)"),
    current_farmer: dict       = Depends(get_current_farmer),
    db:             Database   = Depends(get_db),
):
    # 1. Validate crop
    if crop not in CLASS_MAPPINGS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported crop: '{crop}'. Supported: {sorted(CLASS_MAPPINGS.keys())}",
        )

    # 2. Validate file type
    _validate_image(image)

    # 3. Read bytes once
    contents = await image.read()

    # 4. Decode image
    img_np = _decode_image(contents)

    # 5. Save image to filesystem (binary NOT stored in MongoDB — only reference)
    detection_id = str(uuid.uuid4())
    filename     = image.filename or "image.jpg"
    try:
        saved_filename, saved_path = await _save_image(contents, detection_id, filename)
    except HTTPException:
        raise
    except Exception as exc:
        logger.warning("Could not save image: %s", exc)
        saved_filename = None
        saved_path     = None

    # 6. Run ML prediction (in thread pool)
    try:
        result = await run_prediction(crop, img_np)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))
    except Exception as exc:
        logger.exception("ML prediction error: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during disease detection.",
        )

    # 7. Build prediction_status
    prediction_status = _determine_prediction_status(result.is_uncertain, crop)

    # 8. Build MongoDB document
    now = datetime.now(timezone.utc)
    doc = {
        "detection_id":      detection_id,
        "farmer_id":         current_farmer["farmer_id"],
        "crop_name":         result.crop,
        "predicted_disease": result.disease,
        "confidence":        round(result.confidence, 4),
        "is_uncertain":      result.is_uncertain,
        "severity":          result.severity,
        "prediction_status": prediction_status,
        "image_reference": {          # EMBEDDED sub-document (not the binary)
            "filename": saved_filename,
            "path":     saved_path,
        },
        "diagnosis_details": {        # EMBEDDED denormalized for fast retrieval
            "cause":               result.cause,
            "remedy":              result.remedy,
            "impact":              result.impact,
            "symptoms":            result.symptoms,
            "preventive_measures": result.preventive_measures,
        },
        "uncertainty_message": result.uncertainty_message,
        "detected_at":         now,
    }

    # 9. Insert to MongoDB + update farmer stats (both sync, in executor)
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, lambda: _insert_and_update_stats(db, doc, current_farmer["farmer_id"]))

    return DetectionResponse(
        detection_id        = doc["detection_id"],
        farmer_id           = doc["farmer_id"],
        crop_name           = doc["crop_name"],
        predicted_disease   = doc["predicted_disease"],
        confidence          = doc["confidence"],
        is_uncertain        = doc["is_uncertain"],
        severity            = doc["severity"],
        prediction_status   = doc["prediction_status"],
        diagnosis           = DiagnosisDetail(**doc["diagnosis_details"]),
        image_reference     = ImageReference(**doc["image_reference"]),
        uncertainty_message = doc.get("uncertainty_message"),
        detected_at         = doc["detected_at"],
    )


def _insert_and_update_stats(db: Database, doc: dict, farmer_id: str) -> None:
    """Insert detection record and atomically update farmer stats."""
    db["detection_history"].insert_one(doc)
    # Update embedded stats sub-document ($inc + $set)
    db["farmers"].update_one(
        {"farmer_id": farmer_id},
        {
            "$inc": {"stats.total_scans": 1},
            "$set": {"stats.last_scan_at": doc["detected_at"]},
        },
    )
    logger.info("Detection %s saved for farmer %s.", doc["detection_id"], farmer_id)
