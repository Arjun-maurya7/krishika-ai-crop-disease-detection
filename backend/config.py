"""
backend/config.py  —  Krishika AI CSE494 MongoDB Project
Application configuration loaded from environment variables via pydantic-settings.
Copy .env.example to .env and fill in your values.
"""

import os
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # ── Application ──────────────────────────────────────────────────────────
    APP_NAME: str    = "Krishika AI — CSE494"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool      = False

    # ── JWT ──────────────────────────────────────────────────────────────────
    JWT_SECRET_KEY:  str = "CHANGE_ME_IN_PRODUCTION_USE_32_CHARS_MIN"
    JWT_ALGORITHM:   str = "HS256"
    JWT_EXPIRE_HOURS: int = 24

    # ── MongoDB ───────────────────────────────────────────────────────────────
    MONGO_URI:     str = "mongodb://localhost:27017"
    MONGO_DB_NAME: str = "krishika_cse494"

    # ── Image Storage ────────────────────────────────────────────────────────
    UPLOAD_DIR:           str        = "uploads"
    MAX_IMAGE_SIZE_MB:    float      = 10.0
    ALLOWED_IMAGE_TYPES:  list[str]  = ["image/jpeg", "image/png", "image/webp"]

    # ── ML ───────────────────────────────────────────────────────────────────
    CONFIDENCE_THRESHOLD: float = 0.60
    WARMUP_ON_START:      bool  = True

    # ── CORS ─────────────────────────────────────────────────────────────────
    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """Return cached Settings instance (reads .env once)."""
    return Settings()
