"""Configuración central de Chapi Local (pydantic-settings)."""
from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore", case_sensitive=False)

    app_name: str = "Chapi Local"

    # Infra
    database_url: str = "postgresql+asyncpg://pguser:pgpass@db:5432/chapi"
    redis_url: str = "redis://redis:6379/0"

    # Control de acceso mínimo (T-102). Vacío => modo abierto (MVP/dev, sin auth);
    # definido => exige la clave en los endpoints de negocio. Auth por usuario: fase 2.
    api_key: str = ""

    # Scraper
    use_mock_scraper: bool = True
    results_dir: str = "results"

    # Politeness/rate limiting hacia la fuente (T-104). Efectivo con el scraper
    # real (fase 2): intervalo mínimo entre peticiones + jitter y reintentos.
    scraper_min_delay_seconds: float = 1.0
    scraper_jitter_seconds: float = 0.5
    scraper_max_retries: int = 3
    scraper_backoff_base_seconds: float = 1.0
    scraper_user_agent: str = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    )
    scraper_detail_timeout_ms: int = 10000
    scraper_headless: bool = True

    # arq: el scraper real es lento; sube el timeout del job (part. de T-65).
    arq_job_timeout_seconds: int = 1800

    # NLP (T-210). Mock (rule-based) por defecto; llama-cpp real es opt-in (fase 2).
    use_mock_nlp: bool = True
    enable_summary: bool = True
    llama_model_path: str = "./models/llama-q4.gguf"
    llama_n_ctx: int = 4096

    # Embeddings / búsqueda semántica (T-211/T-212). Mock (hashing) por defecto;
    # sentence-transformers real es opt-in (fase 2, requirements-ml.txt).
    use_mock_embeddings: bool = True
    enable_semantic_search: bool = True
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    embedding_dim: int = 64

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

# Sufijo de los ids de tabla en el modal de detalle por competencia
# (p.ej. #litigantesPen / #relacionesPen). Pen (crawler_nom.py) y Lab (detalle.py)
# están confirmados; Civ y Cob deben verificarse contra el DOM vivo (T-202).
COMPETENCIA_SUFIJO: dict[str, str] = {
    "Penal": "Pen",     # confirmado
    "Laboral": "Lab",   # confirmado
    "Civil": "Civ",     # TODO(fase-2): verificar sufijo real del modal
    "Cobranza": "Cob",  # TODO(fase-2): verificar sufijo real del modal
}
