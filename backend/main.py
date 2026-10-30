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

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
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

    # 5. Warm up VGG19 in background thread
    if settings.WARMUP_ON_START:
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
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
        "db":       settings.MONGO_DB_NAME,
    }


# ── Serve uploaded images as static files ────────────────────────────────────
uploads_path = Path(settings.UPLOAD_DIR)
uploads_path.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(uploads_path)), name="uploads")


# ── Run directly ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8001,        # 8001 to avoid collision with original backend on 8000
        reload=True,
        reload_dirs=["."],
    )
