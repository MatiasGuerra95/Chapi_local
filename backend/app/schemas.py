"""Schemas Pydantic v2 con gating de compliance (finalidad legítima obligatoria)."""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.config import COMPETENCIAS, DEFAULT_COMPETENCIAS, settings


class SubjectIn(BaseModel):
    tipo: str = "persona"
    nombre: str = Field(min_length=1)
    ape_paterno: str = Field(default="", min_length=0)
    ape_materno: str = ""
    rut: Optional[str] = None
    razon_social: Optional[str] = None


class ConsultaCreate(BaseModel):
    subject: SubjectIn
    requested_by: str = Field(min_length=1, description="Usuario que realiza la consulta")
    # Finalidad legítima obligatoria: sin motivo no hay búsqueda.
    motivo: str = Field(min_length=10, description="Finalidad legítima de la consulta")
    competencias: list[str] = Field(default_factory=lambda: list(DEFAULT_COMPETENCIAS))
    year_from: int = settings.default_year_from
    year_to: int = settings.default_year_to

    @field_validator("motivo")
    @classmethod
    def _motivo_no_trivial(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 10:
            raise ValueError("El motivo (finalidad legítima) es obligatorio y debe ser descriptivo.")
        return v

    @field_validator("competencias")
    @classmethod
    def _competencias_validas(cls, v: list[str]) -> list[str]:
        if not v:
            raise ValueError("Debe indicar al menos una competencia.")
        invalidas = [c for c in v if c not in COMPETENCIAS]
        if invalidas:
            raise ValueError(
                f"Competencias no soportadas: {invalidas}. Válidas: {list(COMPETENCIAS)}"
            )
        return v

    @model_validator(mode="after")
    def _rango_anios(self):
        if self.year_from > self.year_to:
            raise ValueError("year_from no puede ser mayor que year_to.")
        return self


class SubjectOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    tipo: str
    nombre: str
    ape_paterno: str
    ape_materno: str
    rut: Optional[str] = None
    razon_social: Optional[str] = None


class CaseResultOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    competencia: Optional[str] = None
    rit: Optional[str] = None
    ruc: Optional[str] = None
    tribunal: Optional[str] = None
    caratulado: Optional[str] = None
    fecha_ingreso: Optional[str] = None
    estado: Optional[str] = None
    year: Optional[int] = None
    possible_homonym: bool = False
    litigantes: list = Field(default_factory=list)
    relaciones: list = Field(default_factory=list)
    source_url: Optional[str] = None


class ConsultaOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    status: str
    requested_by: str
    motivo: str
    fuente: str
    params: dict
    risk_score: Optional[float] = None
    risk_level: Optional[str] = None
    created_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    subject: SubjectOut


class ConsultaDetailOut(ConsultaOut):
    cases: list[CaseResultOut] = Field(default_factory=list)
    counts: dict[str, int] = Field(default_factory=dict)
    homonym_count: int = 0


class AuditOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    consulta_id: Optional[uuid.UUID] = None
    usuario: str
    motivo: Optional[str] = None
    sujeto: str
    fuente: str
    action: str
    params: dict = Field(default_factory=dict)
    created_at: Optional[datetime] = None
