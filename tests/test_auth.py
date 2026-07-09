"""T-220: unit de auth_service (hashing pbkdf2 + JWT) y RBAC. Sin BD."""
import asyncio

import jwt
import pytest
from fastapi import HTTPException

from app import models
from app.config import settings
from app.security import require_role
from app.services import auth_service


def test_hash_verify_roundtrip():
    h = auth_service.hash_password("s3creta-larga")
    assert h.startswith("pbkdf2_sha256$")
    assert auth_service.verify_password("s3creta-larga", h) is True
    assert auth_service.verify_password("otra", h) is False


def test_hash_salt_distinto_por_llamada():
    assert auth_service.hash_password("x12345678") != auth_service.hash_password("x12345678")


def test_verify_password_hash_corrupto():
    assert auth_service.verify_password("x", "no-es-un-hash") is False


def test_token_roundtrip(monkeypatch):
    monkeypatch.setattr(settings, "jwt_secret", "test-secret-de-32-bytes-o-mas-para-hs256")
    token = auth_service.create_access_token("ana", "admin")
    payload = auth_service.decode_token(token)
    assert payload["sub"] == "ana"
    assert payload["role"] == "admin"


def test_token_secreto_incorrecto_falla(monkeypatch):
    monkeypatch.setattr(settings, "jwt_secret", "secret-a-de-32-bytes-o-mas-para-hs256!")
    token = auth_service.create_access_token("ana", "analyst")
    monkeypatch.setattr(settings, "jwt_secret", "secret-b-de-32-bytes-o-mas-para-hs256!")
    with pytest.raises(jwt.PyJWTError):
        auth_service.decode_token(token)


def test_token_expirado(monkeypatch):
    monkeypatch.setattr(settings, "jwt_secret", "test-secret-de-32-bytes-o-mas-para-hs256")
    monkeypatch.setattr(settings, "access_token_expire_minutes", -1)  # ya expirado
    token = auth_service.create_access_token("ana", "analyst")
    with pytest.raises(jwt.ExpiredSignatureError):
        auth_service.decode_token(token)


def test_require_role_permite_y_rechaza():
    dep = require_role("admin")
    admin = models.User(username="a", password_hash="x", role="admin", is_active=True)
    analyst = models.User(username="b", password_hash="x", role="analyst", is_active=True)
    assert asyncio.run(dep(user=admin)) is admin
    with pytest.raises(HTTPException) as exc:
        asyncio.run(dep(user=analyst))
    assert exc.value.status_code == 403
