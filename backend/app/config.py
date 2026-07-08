"""Configuración central de Chapi Local (pydantic-settings)."""
from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore", case_sensitive=False)

    app_name: str = "Chapi Local"

    # Infra
    database_url: str = "postgresql+asyncpg://pguser:pgpass@db:5432/chapi"
    redis_url: str = "redis://redis:6379/0"

    # Scraper
    use_mock_scraper: bool = True
    results_dir: str = "results"

    # Rango de años por defecto (configurable por consulta)
    default_year_from: int = 2018
    default_year_to: int = 2024

    # Trazabilidad
    fuente: str = "Poder Judicial - Oficina Judicial Virtual (OJV)"


settings = Settings()

# Competencias soportadas en "Búsqueda por Nombre" de la OJV.
# value = valor real del <option> en #nomCompetencia.
#   Laboral="4" y Penal="5" están confirmados en el código existente
#   (detalle.py y crawler_nom.py). Civil y Cobranza deben verificarse
#   contra el DOM vivo antes de habilitar el scraper real (fase 2).
COMPETENCIAS: dict[str, str] = {
    "Civil": "3",      # TODO(fase-2): verificar value real en #nomCompetencia
    "Laboral": "4",    # confirmado
    "Penal": "5",      # confirmado
    "Cobranza": "7",   # TODO(fase-2): verificar value real en #nomCompetencia
}

DEFAULT_COMPETENCIAS: list[str] = list(COMPETENCIAS.keys())
