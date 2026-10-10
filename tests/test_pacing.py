"""Shared request pacing and server-directed backoff."""

import asyncio
import time

from custom_components.nio_telematics.pacing import NioRequestPacer


async def test_concurrent_requests_are_serialized() -> None:
    starts: list[float] = []
    pacer = NioRequestPacer(0.02)

    async def request() -> None:
        await pacer.wait()
        starts.append(time.monotonic())

    await asyncio.gather(request(), request(), request())
    assert len(starts) == 3
    assert all(
        later - earlier >= 0.019
        for earlier, later in zip(starts, starts[1:], strict=False)
    )


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


async def test_rate_limit_can_extend_an_already_waiting_request(monkeypatch) -> None:
    clock = [0.0]
    sleeping = asyncio.Event()
    release = asyncio.Event()
    waits = 0

    async def advance(seconds: float) -> None:
        nonlocal waits
        waits += 1
        if waits == 1:
            sleeping.set()
            await release.wait()
        clock[0] += seconds

    monkeypatch.setattr(
        "custom_components.nio_telematics.pacing.time.monotonic", lambda: clock[0]
    )
    monkeypatch.setattr(
        "custom_components.nio_telematics.pacing.asyncio.sleep", advance
    )
    pacer = NioRequestPacer(15)
    await pacer.wait()
    waiter = asyncio.create_task(pacer.wait())
    await sleeping.wait()
    await pacer.rate_limited(45)
    release.set()
    await waiter
    assert waits == 2
    assert clock[0] == 45
