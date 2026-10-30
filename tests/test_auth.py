"""
tests/test_auth.py  —  Krishika AI CSE494 MongoDB Project
Tests for authentication service (no MongoDB required).
"""

import os
import sys
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.services.auth_service import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


# ── Password hashing ──────────────────────────────────────────────────────────

def test_hash_password_produces_hash():
    hashed = hash_password("mysecretpassword")
    assert hashed != "mysecretpassword"
    assert len(hashed) > 20


def test_verify_password_correct():
    hashed = hash_password("testpass123")
    assert verify_password("testpass123", hashed) is True


def test_verify_password_wrong():
    hashed = hash_password("testpass123")
    assert verify_password("wrongpass", hashed) is False


def test_hash_produces_different_hashes():
    """bcrypt salt ensures two hashes of the same password differ."""
    h1 = hash_password("same")
    h2 = hash_password("same")
    assert h1 != h2


# ── JWT ───────────────────────────────────────────────────────────────────────

def test_create_and_decode_token():
    payload = {"sub": "farmer-uuid-123", "name": "Ramesh"}
    token   = create_access_token(payload)
    decoded = decode_access_token(token)
    assert decoded["sub"]  == "farmer-uuid-123"
    assert decoded["name"] == "Ramesh"
    assert "exp" in decoded


def test_decode_invalid_token_raises():
    from jose import JWTError
    with pytest.raises(JWTError):
        decode_access_token("this.is.not.valid")


def test_decode_tampered_token_raises():
    from jose import JWTError
    token    = create_access_token({"sub": "abc"})
    tampered = token[:-5] + "XXXXX"
    with pytest.raises(JWTError):
        decode_access_token(tampered)
