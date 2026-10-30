"""
tests/test_api.py  —  Krishika AI CSE494 MongoDB Project
Integration tests for FastAPI endpoints (requires MongoDB + running app).
"""

import os
import sys
import uuid
import io

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# ── Auth endpoints ────────────────────────────────────────────────────────────

def test_register_success(client):
    resp = client.post("/api/auth/register", json={
        "name":               "Integration Farmer",
        "email":              f"int_{uuid.uuid4().hex[:8]}@test.com",
        "password":           "pass123456",
        "preferred_language": "en",
        "location_state":     "Haryana",
        "location_district":  "Karnal",
    })
    assert resp.status_code == 201
    data = resp.json()
    assert "access_token" in data
    assert data["farmer"]["name"] == "Integration Farmer"
    assert data["farmer"]["location"]["state"] == "Haryana"
    assert data["farmer"]["stats"]["total_scans"] == 0


def test_register_duplicate_email(client, auth_headers):
    """Re-registering with same email must return 409."""
    # Use a fixed email so we can register it twice
    email = f"dup_{uuid.uuid4().hex[:6]}@test.com"
    payload = {"name": "A", "email": email, "password": "pass12345"}
    client.post("/api/auth/register", json=payload)
    resp = client.post("/api/auth/register", json=payload)
    assert resp.status_code == 409


def test_register_short_password_rejected(client):
    resp = client.post("/api/auth/register", json={
        "name": "Farmer", "email": "short@test.com", "password": "short",
    })
    assert resp.status_code == 422


def test_login_success(client):
    email = f"login_{uuid.uuid4().hex[:6]}@test.com"
    client.post("/api/auth/register", json={
        "name": "Login Test", "email": email, "password": "pass12345678",
    })
    resp = client.post("/api/auth/login", json={"email": email, "password": "pass12345678"})
    assert resp.status_code == 200
    assert "access_token" in resp.json()


def test_login_wrong_password(client):
    email = f"badpw_{uuid.uuid4().hex[:6]}@test.com"
    client.post("/api/auth/register", json={
        "name": "Wrong PW", "email": email, "password": "correctpassword",
    })
    resp = client.post("/api/auth/login", json={"email": email, "password": "wrongpassword"})
    assert resp.status_code == 401


def test_get_me(client, auth_headers):
    resp = client.get("/api/auth/me", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "farmer_id" in data
    assert "email"     in data


# ── Crop endpoints ────────────────────────────────────────────────────────────

def test_list_crops(client):
    resp = client.get("/api/crops")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 17
    assert len(data["crops"]) == 17


def test_get_crop_with_diseases(client):
    resp = client.get("/api/crops/Tomato/diseases")
    assert resp.status_code == 200
    data = resp.json()
    assert "disease_details" in data
    assert len(data["disease_details"]) >= 5


# ── Disease endpoints ─────────────────────────────────────────────────────────

def test_list_diseases_for_crop(client):
    resp = client.get("/api/diseases?crop=Tomato")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] >= 5


def test_search_diseases_by_severity(client):
    resp = client.get("/api/diseases?severity=high")
    assert resp.status_code == 200
    diseases = resp.json()["diseases"]
    for d in diseases:
        assert d["severity"] == "high"


# ── History endpoints ─────────────────────────────────────────────────────────

def test_history_empty_initially(client, auth_headers):
    resp = client.get("/api/history", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "items" in data
    assert "total" in data
    assert "total_pages" in data


def test_history_requires_auth(client):
    resp = client.get("/api/history")
    assert resp.status_code == 403


# ── Dashboard endpoints ───────────────────────────────────────────────────────

def test_dashboard_requires_auth(client):
    resp = client.get("/api/dashboard")
    assert resp.status_code == 403


def test_dashboard_returns_stats(client, auth_headers):
    resp = client.get("/api/dashboard", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "total_scans"    in data
    assert "healthy_count"  in data
    assert "top_diseases"   in data
    assert "monthly_trend"  in data


def test_global_dashboard(client):
    resp = client.get("/api/dashboard/global")
    assert resp.status_code == 200


# ── Health check ──────────────────────────────────────────────────────────────

def test_health(client):
    resp = client.get("/api/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"
