"""Shared request pacing and server-directed backoff."""

import asyncio

from custom_components.nio_telematics.pacing import NioRequestPacer


async def test_concurrent_requests_are_serialized(monkeypatch) -> None:
    clock = [0.0]
    starts: list[float] = []
    real_sleep = asyncio.sleep

    async def advance(seconds: float) -> None:
        clock[0] += seconds
        await real_sleep(0)

    monkeypatch.setattr(
        "custom_components.nio_telematics.pacing.time.monotonic", lambda: clock[0]
    )
    monkeypatch.setattr(
        "custom_components.nio_telematics.pacing.asyncio.sleep", advance
    )
    pacer = NioRequestPacer(15)

    async def request() -> None:
        await pacer.wait()
        starts.append(clock[0])

    await asyncio.gather(request(), request(), request())
    assert starts == [0.0, 15.0, 30.0]


async def test_retry_after_extends_shared_budget(monkeypatch) -> None:
    clock = [0.0]
    delays: list[float] = []

    async def advance(seconds: float) -> None:
        delays.append(seconds)
        clock[0] += seconds

    monkeypatch.setattr(
        "custom_components.nio_telematics.pacing.time.monotonic", lambda: clock[0]
    )
    monkeypatch.setattr(
        "custom_components.nio_telematics.pacing.asyncio.sleep", advance
    )
    pacer = NioRequestPacer(15)
    await pacer.wait()
    await pacer.rate_limited(45)
    await pacer.wait()
    assert delays == [45]
    pacer.succeeded()
    await pacer.rate_limited(None)
    await pacer.wait()
    assert delays[-1] == 15
