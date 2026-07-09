"""Modelos SQLAlchemy 2.0 (typed) para Chapi Local."""
from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class Subject(Base):
    """Sujeto consultado: persona o empresa."""

    __tablename__ = "subjects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tipo: Mapped[str] = mapped_column(String(16), default="persona")  # persona | empresa
    nombre: Mapped[str] = mapped_column(String(200))
    ape_paterno: Mapped[str] = mapped_column(String(200), default="")
    ape_materno: Mapped[str] = mapped_column(String(200), default="")
    rut: Mapped[str | None] = mapped_column(String(20), nullable=True)
    razon_social: Mapped[str | None] = mapped_column(String(300), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    consultas: Mapped[list["Consulta"]] = relationship(back_populates="subject")


class Consulta(Base):
    """Solicitud de due diligence (una búsqueda con finalidad legítima)."""

    __tablename__ = "consultas"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    subject_id: Mapped[int] = mapped_column(ForeignKey("subjects.id"))

    requested_by: Mapped[str] = mapped_column(String(200))  # usuario
    motivo: Mapped[str] = mapped_column(Text)  # finalidad legítima (obligatoria)
    fuente: Mapped[str] = mapped_column(String(200))
    params: Mapped[dict] = mapped_column(JSONB, default=dict)  # competencias, year_from, year_to

    status: Mapped[str] = mapped_column(String(16), default="pending")  # pending|running|done|error
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    risk_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    risk_level: Mapped[str | None] = mapped_column(String(16), nullable=True)
    results_json_path: Mapped[str | None] = mapped_column(String(500), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), index=True
    )
    started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    subject: Mapped["Subject"] = relationship(back_populates="consultas")
    cases: Mapped[list["CaseResult"]] = relationship(
        back_populates="consulta", cascade="all, delete-orphan"
    )
    reports: Mapped[list["Report"]] = relationship(
        back_populates="consulta", cascade="all, delete-orphan"
    )


class CaseResult(Base):
    """Causa judicial normalizada asociada a una consulta."""

    __tablename__ = "case_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    consulta_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("consultas.id"), index=True)

    competencia: Mapped[str | None] = mapped_column(String(32), nullable=True)
    rit: Mapped[str | None] = mapped_column(String(64), nullable=True)
    ruc: Mapped[str | None] = mapped_column(String(64), nullable=True)
    tribunal: Mapped[str | None] = mapped_column(String(300), nullable=True)
    caratulado: Mapped[str | None] = mapped_column(Text, nullable=True)
    fecha_ingreso: Mapped[str | None] = mapped_column(String(32), nullable=True)
    estado: Mapped[str | None] = mapped_column(String(120), nullable=True)
    year: Mapped[int | None] = mapped_column(Integer, nullable=True)

    litigantes: Mapped[list] = mapped_column(JSONB, default=list)
    relaciones: Mapped[list] = mapped_column(JSONB, default=list)

    possible_homonym: Mapped[bool] = mapped_column(Boolean, default=False)
    source_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    scraped_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    consulta: Mapped["Consulta"] = relationship(back_populates="cases")


class AuditLog(Base):
    """Registro de auditoría append-only (trazabilidad)."""

    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    consulta_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("consultas.id"), nullable=True, index=True
    )
    usuario: Mapped[str] = mapped_column(String(200))
    motivo: Mapped[str | None] = mapped_column(Text, nullable=True)
    sujeto: Mapped[str] = mapped_column(Text)
    fuente: Mapped[str] = mapped_column(String(200))
    action: Mapped[str] = mapped_column(String(64))
    params: Mapped[dict] = mapped_column(JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class Report(Base):
    """Informe HTML generado para una consulta."""

    __tablename__ = "reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    consulta_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("consultas.id"))
    html_path: Mapped[str] = mapped_column(String(500))
    score: Mapped[float | None] = mapped_column(Float, nullable=True)
    level: Mapped[str | None] = mapped_column(String(16), nullable=True)
    generated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    consulta: Mapped["Consulta"] = relationship(back_populates="reports")
