"""
tests/conftest.py  —  Krishika AI CSE494 MongoDB Project
Shared pytest fixtures.
"""

import os
import sys

# Ensure project root is on path for `ml/` and `backend/` imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from fastapi.testclient import TestClient

from backend.main import app


@pytest.fixture(scope="session")
def client():
    """TestClient connected to the FastAPI app (requires MongoDB running)."""
    with TestClient(app, raise_server_exceptions=True) as c:
        yield c


@pytest.fixture(scope="session")
def auth_headers(client):
    """Register a test farmer and return auth headers."""
    import uuid
    email = f"test_{uuid.uuid4().hex[:8]}@krishika-test.com"
    resp  = client.post("/api/auth/register", json={
        "name":               "Test Farmer",
        "email":              email,
        "password":           "testpass123",
        "preferred_language": "en",
    })
    assert resp.status_code == 201, resp.text
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
