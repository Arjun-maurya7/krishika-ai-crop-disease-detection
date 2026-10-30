"""
backend/services/auth_service.py  —  Krishika AI CSE494 MongoDB Project
JWT creation/verification and bcrypt password hashing.
"""

from datetime import datetime, timedelta, timezone
from typing import Any

import bcrypt
from jose import jwt

from backend.config import get_settings


def hash_password(plain: str) -> str:
    """Return bcrypt hash of the given plain-text password."""
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    """Return True if plain matches the stored bcrypt hash."""
    return bcrypt.checkpw(plain.encode(), hashed.encode())


def create_access_token(payload: dict[str, Any]) -> str:
    """
    Create a signed JWT access token with an expiry claim.

    Args:
        payload: Dict of claims to embed (e.g. {"sub": farmer_id})

    Returns:
        Encoded JWT string
    """
    settings = get_settings()
    data     = payload.copy()
    expire   = datetime.now(timezone.utc) + timedelta(hours=settings.JWT_EXPIRE_HOURS)
    data["exp"] = expire
    return jwt.encode(data, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> dict[str, Any]:
    """
    Decode and verify a JWT access token.

    Returns:
        Decoded payload dict

    Raises:
        JWTError: if token is invalid, expired, or has wrong signature
    """
    settings = get_settings()
    return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
