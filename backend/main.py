"""
backend/main.py  —  Krishika AI CSE494 MongoDB Project
FastAPI application factory.

Startup sequence:
  1. PyMongo connection opened and pinged
  2. Collections created with $jsonSchema validators
  3. Indexes created
  4. Crops + diseases seeded (upsert)
  5. ML model warmed up in background thread
"""

import logging
import sys
import threading
from contextlib import asynccontextmanager

sys.path.insert(0, ".")  # ensure project root is on path for `ml/` imports

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from backend.config import get_settings
from backend.database.collections import ensure_collections_and_indexes
from backend.database.connection import close_db, connect_db, get_db
from backend.routes import auth, crops, dashboard, detection, history

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
)
logger   = logging.getLogger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # ── STARTUP ───────────────────────────────────────────────────────────────
    logger.info("Starting Krishika AI CSE494 backend …")

    # 1. Connect MongoDB (PyMongo sync)
    connect_db(settings.MONGO_URI, settings.MONGO_DB_NAME)
    db = get_db(settings.MONGO_DB_NAME)

    # 2. Create collections + schema validators + indexes
    ensure_collections_and_indexes(db)

    # 3. Seed reference data
    from scripts.seed_db import run_seed
    run_seed(db)

    # 4. Create uploads directory
    Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)

    # 5. Warm up VGG19 before the first diagnosis. On hosted deployments the
    # first request must not carry the full model download and initialization.
    if settings.WARMUP_ON_START or not settings.DEBUG:
        import ml.predictor as predictor
        t = threading.Thread(target=predictor.warmup, daemon=True, name="ml-warmup")
        t.start()
        logger.info("ML model warmup started in background thread.")

    logger.info("Krishika AI CSE494 backend is ready on port 8001 🌿")
    yield

    # ── SHUTDOWN ──────────────────────────────────────────────────────────────
    close_db()
    logger.info("Krishika AI CSE494 backend shut down cleanly.")


app = FastAPI(
    title="Krishika AI — CSE494 MongoDB API",
    description=(
        "Crop Disease Detection System powered by VGG19 + SVM.\n\n"
        "CSE494 — Intelligent NoSQL Databases (MongoDB) course project.\n\n"
        "**Note:** Disease predictions are general guidance only. "
        "Always consult a licensed agronomist before applying treatment."
    ),
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# ── CORS ──────────────────────────────────────────────────────────────────────
# Origins are loaded entirely from the CORS_ORIGINS environment variable.
# Set CORS_ORIGINS in .env or in the EC2 environment (see .env.example).
cors_origins = list(settings.CORS_ORIGINS)
cors_config = {
    "allow_origins": cors_origins,
    "allow_credentials": False,
    "allow_methods": ["*"],
    "allow_headers": ["*"],
}

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(auth.router)
app.include_router(detection.router)
app.include_router(history.router)
app.include_router(dashboard.router)
app.include_router(crops.router)


# ── Health check ──────────────────────────────────────────────────────────────
@app.get("/api/health", tags=["System"])
async def health():
    import ml.predictor as predictor
    return {
        "status":   "ok",
        "version":  settings.APP_VERSION,
        "ml_ready": predictor._model_ready,
        "ml_loading": predictor._model_loading,
        "db":       settings.MONGO_DB_NAME,
    }


@app.get("/", tags=["System"], include_in_schema=False)
async def root():
    """Provide a simple liveness response for platform probes."""
    return {"status": "ok", "health_url": "/api/health"}


@app.exception_handler(Exception)
async def handle_unexpected_error(request: Request, exc: Exception):
    logger.exception("Unhandled API error for %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected server error occurred."},
    )


# ── Serve uploaded images as static files ────────────────────────────────────
uploads_path = Path(settings.UPLOAD_DIR)
uploads_path.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(uploads_path)), name="uploads")

# Wrap the complete FastAPI application so CORS headers are added to unhandled
# error responses as well as normal and HTTPException responses.
app = CORSMiddleware(app, **cors_config)


# ── Run directly ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=settings.PORT,
        reload=settings.DEBUG,   # reload only in DEBUG mode
    )
