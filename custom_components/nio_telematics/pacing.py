"""Per-application pacing for NIO vehicle requests."""

from __future__ import annotations

import asyncio
import time


class NioRequestPacer:
    """Serialize request starts, including concurrent vehicles and manual refreshes."""

    def __init__(self, interval: float = 15.0) -> None:
        self.interval = interval
        self._lock = asyncio.Lock()
        self._next_at = 0.0
        self._rate_failures = 0

    async def wait(self) -> None:
        async with self._lock:
            delay = max(0.0, self._next_at - time.monotonic())
            if delay:
                await asyncio.sleep(delay)
            self._next_at = time.monotonic() + self.interval

    async def rate_limited(self, retry_after: float | None) -> None:
        """Honor server delay, with bounded exponential fallback."""
        async with self._lock:
            self._rate_failures += 1
            fallback = min(15.0 * 2 ** (self._rate_failures - 1), 300.0)
            self._next_at = max(
                self._next_at,
                time.monotonic() + max(retry_after or 0.0, fallback),
            )

    def succeeded(self) -> None:
        self._rate_failures = 0
