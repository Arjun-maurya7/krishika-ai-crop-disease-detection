"""
backend/database/connection.py  —  Krishika AI CSE494 MongoDB Project

PyMongo synchronous client singleton.

Academic note:
  This project uses PyMongo (synchronous) deliberately to demonstrate
  direct MongoDB operations as taught in CSE494.  The original Krishika AI
  app (backend/) uses Motor for async performance; here we keep it simple
  and readable for the course submission.
  
  FastAPI routes call run_in_executor() to offload PyMongo blocking I/O
  to a thread pool, keeping the ASGI event loop responsive.
"""

import logging
from typing import Optional

from pymongo import MongoClient
from pymongo.database import Database

logger = logging.getLogger(__name__)

_client: Optional[MongoClient] = None


def connect_db(uri: str, db_name: str) -> None:
    """
    Open the PyMongo connection pool.
    Called once at application startup.

    Args:
        uri:     MongoDB connection string
        db_name: Database to use
    """
    global _client
    logger.info("Connecting to MongoDB (PyMongo) at %s …", uri)
    _client = MongoClient(uri, serverSelectionTimeoutMS=5000)
    # Ping to verify
    _client.admin.command("ping")
    logger.info("MongoDB connection established — database: %s", db_name)


def close_db() -> None:
    """Close the PyMongo connection pool. Called at application shutdown."""
    global _client
    if _client is not None:
        _client.close()
        _client = None
        logger.info("MongoDB connection closed.")


def get_client() -> MongoClient:
    """Return the raw PyMongo client. Raises if not connected."""
    if _client is None:
        raise RuntimeError("Database not connected. Call connect_db() first.")
    return _client


def get_db(db_name: str) -> Database:
    """Return the named database from the active client."""
    return get_client()[db_name]
