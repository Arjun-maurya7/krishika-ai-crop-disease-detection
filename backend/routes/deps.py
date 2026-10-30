"""
backend/routes/deps.py  —  Krishika AI CSE494 MongoDB Project
Shared FastAPI dependencies: DB getter, current farmer extractor.
"""

import asyncio
import logging
from typing import Any

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from pymongo.database import Database

from backend.config import get_settings
from backend.database.connection import get_db as _get_db
from backend.services.auth_service import decode_access_token

logger = logging.getLogger(__name__)
_bearer = HTTPBearer(auto_error=True)


def get_db() -> Database:
    """FastAPI dependency that returns the PyMongo database."""
    settings = get_settings()
    return _get_db(settings.MONGO_DB_NAME)


async def get_current_farmer(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
    db: Database = Depends(get_db),
) -> dict:
    """
    FastAPI dependency that decodes the Bearer JWT and returns the farmer document.

    Raises HTTP 401 if token is invalid / farmer not found.
    """
    token = credentials.credentials
    try:
        payload  = decode_access_token(token)
        farmer_id: str = payload.get("sub", "")
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # PyMongo query runs in thread pool
    loop   = asyncio.get_event_loop()
    farmer = await loop.run_in_executor(
        None,
        lambda: db["farmers"].find_one({"farmer_id": farmer_id}, {"_id": 0}),
    )
    if farmer is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Farmer account not found.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return farmer
