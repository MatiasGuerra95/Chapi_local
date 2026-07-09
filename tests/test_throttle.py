"""T-104: RateLimiter y retry_async con reloj/sleep inyectados (deterministas)."""
import asyncio

import pytest

from app.services.throttle import RateLimiter, retry_async


class FakeClock:
    """Reloj virtual: ``sleep`` avanza el tiempo sin esperar real."""

    def __init__(self):
        self.t = 0.0
        self.slept: list[float] = []

    def now(self) -> float:
        return self.t

    async def sleep(self, secs: float) -> None:
        self.slept.append(secs)
        self.t += secs


def test_ratelimiter_primera_llamada_no_espera():
    clk = FakeClock()
    rl = RateLimiter(min_interval=2.0, now=clk.now, sleep=clk.sleep)

    async def go():
        return await rl.acquire()

    assert asyncio.run(go()) == 0.0
    assert clk.slept == []


def test_ratelimiter_respeta_intervalo_minimo():
    clk = FakeClock()
    rl = RateLimiter(min_interval=2.0, now=clk.now, sleep=clk.sleep)

    async def go():
        await rl.acquire()          # t=0, no espera; _last=0
        # Sin avanzar el reloj, la 2ª llamada debe esperar el intervalo completo.
        return await rl.acquire()

    waited = asyncio.run(go())
    assert waited == pytest.approx(2.0)
    assert clk.slept == [pytest.approx(2.0)]


def test_ratelimiter_no_espera_si_ya_paso_el_intervalo():
    clk = FakeClock()
    rl = RateLimiter(min_interval=1.0, now=clk.now, sleep=clk.sleep)

    async def go():
        await rl.acquire()
        clk.t += 5.0  # pasó más que el intervalo
        return await rl.acquire()

    assert asyncio.run(go()) == 0.0


def test_retry_async_reintenta_y_finalmente_tiene_exito():
    clk = FakeClock()
    calls = {"n": 0}

    async def flaky():
        calls["n"] += 1
        if calls["n"] < 3:
            raise ValueError("transitorio")
        return "ok"

    async def go():
        return await retry_async(
            flaky, retries=3, base_delay=1.0, factor=2.0, sleep=clk.sleep
        )

    assert asyncio.run(go()) == "ok"
    assert calls["n"] == 3
    # Backoff exponencial: tras el 1er y 2do fallo → 1.0 y 2.0 s.
    assert clk.slept == [pytest.approx(1.0), pytest.approx(2.0)]


def test_retry_async_agota_intentos_y_relanza():
    clk = FakeClock()

    async def siempre_falla():
        raise RuntimeError("boom")

    async def go():
        await retry_async(siempre_falla, retries=2, base_delay=0.5, sleep=clk.sleep)

    with pytest.raises(RuntimeError):
        asyncio.run(go())
    # 2 reintentos => 2 esperas (0.5, 1.0); el 3er intento falla y re-lanza.
    assert clk.slept == [pytest.approx(0.5), pytest.approx(1.0)]
