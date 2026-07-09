#!/usr/bin/env python3
"""Alta de usuarios internos (T-220). Bootstrap del primer admin.

Corre dentro del contenedor (tiene la app + acceso a la BD):
    docker compose exec api python /app/scripts/create_user.py \
        --username admin --password 'CAMBIA_ESTO' --role admin
"""
from __future__ import annotations

import argparse
import asyncio

from sqlalchemy import select

from app import models
from app.db import SessionLocal, init_models
from app.services import auth_service


async def main(args: argparse.Namespace) -> int:
    await init_models()
    async with SessionLocal() as session:
        existing = (
            await session.execute(
                select(models.User).where(models.User.username == args.username)
            )
        ).scalar_one_or_none()
        if existing:
            print(f"El usuario '{args.username}' ya existe.")
            return 1
        session.add(
            models.User(
                username=args.username,
                password_hash=auth_service.hash_password(args.password),
                role=args.role,
            )
        )
        await session.commit()
        print(f"Usuario '{args.username}' creado con rol '{args.role}'.")
        return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Crear usuario interno (T-220)")
    ap.add_argument("--username", required=True)
    ap.add_argument("--password", required=True)
    ap.add_argument("--role", default="analyst", choices=["analyst", "admin"])
    raise SystemExit(asyncio.run(main(ap.parse_args())))
