"""Endpoints de autenticación de usuarios internos (T-220)."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app import models, schemas
from app.config import settings
from app.db import get_session
from app.security import get_current_user, require_role
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/token", response_model=schemas.TokenOut)
async def login(payload: schemas.LoginIn, session: AsyncSession = Depends(get_session)):
    """Login por usuario/contraseña; devuelve un JWT."""
    if not settings.jwt_secret:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Autenticación no configurada (falta JWT_SECRET).",
        )
    user = (
        await session.execute(
            select(models.User).where(models.User.username == payload.username)
        )
    ).scalar_one_or_none()
    if user is None or not user.is_active or not auth_service.verify_password(
        payload.password, user.password_hash
    ):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales inválidas.")
    token = auth_service.create_access_token(user.username, user.role)
    return schemas.TokenOut(access_token=token)


@router.get("/me", response_model=schemas.UserOut)
async def me(user: models.User = Depends(get_current_user)):
    return user


@router.post("/users", response_model=schemas.UserOut, status_code=status.HTTP_201_CREATED)
async def create_user(
    payload: schemas.UserCreate,
    session: AsyncSession = Depends(get_session),
    _admin: models.User = Depends(require_role("admin")),
):
    """Alta de usuario (sólo admin)."""
    exists = (
        await session.execute(
            select(models.User).where(models.User.username == payload.username)
        )
    ).scalar_one_or_none()
    if exists:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El usuario ya existe.")
    user = models.User(
        username=payload.username,
        password_hash=auth_service.hash_password(payload.password),
        role=payload.role,
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user
