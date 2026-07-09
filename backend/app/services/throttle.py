"""Politeness / rate limiting hacia la fuente (T-104, RNF-03/RNF-08).

Utilidades reutilizables para que el scraper real sea "amable" con la OJV del
Poder Judicial (prerequisito del scraper real, fase 2):

- ``RateLimiter``: garantiza un intervalo mínimo entre peticiones sucesivas, con
  un *jitter* aleatorio opcional para no golpear con un patrón fijo.
- ``retry_async``: reintentos con *backoff* exponencial ante fallos transitorios.

El reloj y el ``sleep`` se inyectan para poder testear de forma determinista sin
esperar tiempo real.
"""
from __future__ import annotations

import asyncio
import random
import time
from typing import Awaitable, Callable, Sequence, TypeVar

T = TypeVar("T")

Now = Callable[[], float]
Sleep = Callable[[float], Awaitable[None]]


class RateLimiter:
    """Impone un intervalo mínimo (+ jitter) entre llamadas sucesivas a ``acquire``."""

    def __init__(
        self,
        min_interval: float,
        jitter: float = 0.0,
        *,
        now: Now | None = None,
        sleep: Sleep | None = None,
    ) -> None:
        self.min_interval = max(0.0, float(min_interval))
        self.jitter = max(0.0, float(jitter))
        self._now = now or time.monotonic
        self._sleep = sleep or asyncio.sleep
        self._last: float | None = None

    async def acquire(self) -> float:
        """Espera lo necesario para respetar el intervalo. Devuelve los segundos esperados."""
        waited = 0.0
        if self._last is not None:
            target = self._last + self.min_interval
            if self.jitter:
                target += random.uniform(0.0, self.jitter)
            waited = max(0.0, target - self._now())
            if waited > 0:
                await self._sleep(waited)
        self._last = self._now()
        return waited


async def retry_async(
    fn: Callable[[], Awaitable[T]],
    *,
    retries: int = 3,
    base_delay: float = 1.0,
    factor: float = 2.0,
    max_delay: float = 30.0,
    exceptions: Sequence[type[BaseException]] = (Exception,),
    sleep: Sleep | None = None,
) -> T:
    """Ejecuta ``fn`` con reintentos y backoff exponencial ante ``exceptions``.

    Reintenta hasta ``retries`` veces (``retries + 1`` intentos en total). Re-lanza
    la última excepción si se agotan los intentos.
    """
    _sleep = sleep or asyncio.sleep
    exc_tuple = tuple(exceptions)
    attempt = 0
    while True:
        try:
            return await fn()
        except exc_tuple:
            attempt += 1
            if attempt > retries:
                raise
            delay = min(max_delay, base_delay * (factor ** (attempt - 1)))
            await _sleep(delay)
