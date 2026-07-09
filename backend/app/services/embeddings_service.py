"""Embeddings para búsqueda semántica (T-211, F2.B).

Patrón mock/real como el resto de los servicios:
- ``MockEmbedder``: embedding determinista por *hashing* de tokens (bag-of-words),
  sin dependencias ML. Da similitud coseno útil (léxica) y es testeable.
- ``SentenceTransformerEmbedder``: skeleton fase 2 con import perezoso de
  ``sentence_transformers`` (opt-in ``USE_MOCK_EMBEDDINGS=false``,
  ``requirements-ml.txt``).

La persistencia a escala con **pgvector** (índice entre consultas) requiere una
imagen Postgres con la extensión (``docker-compose.pgvector.yml``) y se deja como
paso siguiente; el endpoint de T-212 rankea en memoria sobre una consulta.
"""
from __future__ import annotations

import hashlib
import math
import re
from typing import Protocol, runtime_checkable

from app.config import settings

_TOKEN_RE = re.compile(r"[a-z0-9áéíóúñ]+")


def _tokens(text: str) -> list[str]:
    return _TOKEN_RE.findall((text or "").lower())


@runtime_checkable
class Embedder(Protocol):
    def embed(self, text: str) -> list[float]:
        ...


class MockEmbedder:
    """Embedding determinista por hashing de tokens, L2-normalizado (sin ML)."""

    def __init__(self, dim: int | None = None) -> None:
        self.dim = dim or settings.embedding_dim

    def embed(self, text: str) -> list[float]:
        vec = [0.0] * self.dim
        for tok in _tokens(text):
            bucket = int(hashlib.md5(tok.encode()).hexdigest(), 16) % self.dim
            vec[bucket] += 1.0
        norm = math.sqrt(sum(v * v for v in vec))
        if norm:
            vec = [v / norm for v in vec]
        return vec


class SentenceTransformerEmbedder:
    """Skeleton fase 2: embeddings con sentence-transformers (requiere ML stack)."""

    def __init__(self) -> None:
        self._model = None

    def _get(self):
        if self._model is None:
            from sentence_transformers import SentenceTransformer  # import perezoso

            self._model = SentenceTransformer(settings.embedding_model)
        return self._model

    def embed(self, text: str) -> list[float]:
        return [float(x) for x in self._get().encode(text or "", normalize_embeddings=True)]


def cosine(a: list[float], b: list[float]) -> float:
    """Similitud coseno. Asume vectores de igual dimensión."""
    if not a or not b:
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if not na or not nb:
        return 0.0
    return dot / (na * nb)


_embedder: Embedder | None = None


def get_embedder() -> Embedder:
    """Factory: mock por defecto, sentence-transformers cuando USE_MOCK_EMBEDDINGS=false."""
    global _embedder
    if _embedder is None:
        _embedder = (
            MockEmbedder() if settings.use_mock_embeddings else SentenceTransformerEmbedder()
        )
    return _embedder
