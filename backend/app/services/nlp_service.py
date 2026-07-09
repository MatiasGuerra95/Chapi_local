"""Servicio de NLP: síntesis narrativa de los hallazgos (T-210, F2.B).

Sigue el patrón mock/real del scraper: ``MockSummarizer`` (rule-based, sin ML) es el
default del MVP y es totalmente testeable; ``LlamaCppSummarizer`` es el skeleton de
fase 2 que importa ``llama_cpp`` de forma perezosa (opt-in con ``USE_MOCK_NLP=false``).

Compliance (RC-03): la síntesis se redacta como **indicadores preliminares para
revisión humana**; nunca afirma culpabilidad ni recomienda contratar/no contratar.
"""
from __future__ import annotations

from typing import Any, Protocol, runtime_checkable

from app.config import settings

_ACTIVA_HINTS = ("trami", "activ", "vigente", "en curso")


def _estado(case: Any) -> str:
    val = case.get("estado") if isinstance(case, dict) else getattr(case, "estado", None)
    return (val or "").lower()


def _es_activa(estado: str) -> bool:
    return any(h in estado for h in _ACTIVA_HINTS)


@runtime_checkable
class Summarizer(Protocol):
    def summarize(self, *, cases: list, risk: dict) -> str:
        ...


class MockSummarizer:
    """Síntesis rule-based, determinista y compatible con compliance (sin ML)."""

    def summarize(self, *, cases: list, risk: dict) -> str:
        total = risk.get("total", len(cases))
        if not total:
            return (
                "No se identificaron causas para los parámetros consultados. "
                "Resultado preliminar sujeto a verificación por una persona autorizada."
            )
        counts = risk.get("counts") or {}
        dist = ", ".join(f"{k}: {v}" for k, v in counts.items())
        activos = sum(1 for c in cases if _es_activa(_estado(c)))

        partes = [f"Se identificaron {total} causa(s) asociadas al nombre consultado"]
        if dist:
            partes.append(f" (distribución por competencia: {dist})")
        partes.append(".")
        if activos:
            partes.append(f" {activos} figura(n) con estado activo o en tramitación.")
        if risk.get("homonym_warning"):
            partes.append(
                " Una parte relevante podría corresponder a homónimos; se requiere "
                "verificación por RUT."
            )
        partes.append(f" Nivel de riesgo indicativo: {risk.get('level', 'n/d')}.")
        partes.append(
            " Estos hallazgos son indicadores preliminares para revisión por una "
            "persona autorizada y no constituyen un juicio sobre la persona."
        )
        return "".join(partes)


# Instrucción con restricciones de compliance para el modelo real (fase 2).
_LLAMA_SYSTEM = (
    "Eres un asistente de compliance. Resume en español (<120 palabras) los "
    "hallazgos judiciales como INDICADORES PRELIMINARES para revisión humana. "
    "No afirmes culpabilidad. No recomiendes contratar ni no contratar. Recuerda "
    "que la búsqueda por nombre puede incluir homónimos."
)


class LlamaCppSummarizer:
    """Skeleton fase 2: resumen con llama-cpp. Requiere ``requirements-ml.txt``."""

    def __init__(self) -> None:
        self._llm = None

    def _model(self):
        if self._llm is None:
            from llama_cpp import Llama  # import perezoso (sólo en el path real)

            self._llm = Llama(
                model_path=settings.llama_model_path, n_ctx=settings.llama_n_ctx
            )
        return self._llm

    def summarize(self, *, cases: list, risk: dict) -> str:
        base = MockSummarizer().summarize(cases=cases, risk=risk)
        prompt = f"{_LLAMA_SYSTEM}\n\nDatos: {base}\n\nResumen:"
        out = self._model()(prompt, max_tokens=220, temperature=0.2)
        return out["choices"][0]["text"].strip()


_summarizer: Summarizer | None = None


def get_summarizer() -> Summarizer:
    """Factory: mock por defecto, llama-cpp cuando USE_MOCK_NLP=false."""
    global _summarizer
    if _summarizer is None:
        _summarizer = MockSummarizer() if settings.use_mock_nlp else LlamaCppSummarizer()
    return _summarizer


def generate_summary(cases: list, risk: dict) -> str:
    """Síntesis para el informe. Nunca rompe el informe: ante error devuelve ''."""
    if not settings.enable_summary:
        return ""
    try:
        return get_summarizer().summarize(cases=list(cases), risk=risk)
    except Exception:
        return ""
