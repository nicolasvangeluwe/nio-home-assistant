"""Cache-only Companion transport; never obtains a grant or polls NIO."""

from __future__ import annotations

import asyncio
import json
import math
import re
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from email.utils import parsedate_to_datetime
from time import monotonic
from urllib.parse import urlsplit

from aiohttp import ClientError, ClientSession, ClientTimeout

from .companion_snapshot import (
    CompanionContractError,
    CompanionSnapshot,
    classify_companion_error,
    parse_companion_snapshot,
)
from .models import normalize_vin

_PATH = "/ha/v1/vehicle"
_MAX_BODY = 65536
_CREDENTIAL = re.compile(r"^(?:ha1|hap1)_[A-Za-z0-9_-]{43}$")
_PERSISTENT_CREDENTIAL = re.compile(r"^hap1_[A-Za-z0-9_-]{43}$")
MAX_SOURCE_AGE = timedelta(minutes=15)


def _retry_delay(header: str | None, *, admission: bool = False) -> float | None:
    if header is None:
        return 1 if admission else None
    try:
        seconds = float(header)
    except (TypeError, ValueError):
        try:
            target = parsedate_to_datetime(header)
            seconds = (target - datetime.now(target.tzinfo)).total_seconds()
        except (TypeError, ValueError, OverflowError):
            return 1 if admission else None
    return max(1, min(seconds, 3600)) if math.isfinite(seconds) else None


def is_persistent_credential(value: str) -> bool:
    """Daily HA setup must not silently accept a 24-hour proof credential."""
    return isinstance(value, str) and bool(_PERSISTENT_CREDENTIAL.fullmatch(value))


def field_is_current(field, now: datetime) -> bool:
    """Check original clocks locally, even when a server labels an old field valid."""
    return (
        field.usable
        and field.source_timestamp is not None
        and field.received_at is not None
        and timedelta(0) <= now - field.source_timestamp <= MAX_SOURCE_AGE
        and field.source_timestamp <= field.received_at <= now + timedelta(seconds=30)
    )


class CompanionFetchError(Exception):
    """A safe, non-payload error category for the future HA coordinator."""

    def __init__(
        self,
        kind: str,
        *,
        reason: str | None = None,
        status: int | None = None,
        retry_after: float | None = None,
        duration_ms: int | None = None,
    ) -> None:
        self.kind = kind
        self.reason = reason
        self.status = status
        self.retry_after = retry_after
        self.duration_ms = duration_ms
        super().__init__(kind)


@dataclass(frozen=True, slots=True)
class CompanionCandidate:
    """Validated read-only source candidate; no HA entry was changed."""

    snapshot: CompanionSnapshot
    required_fields: tuple[str, ...]


class CompanionVehicleClient:
    """Read one owner-bound cached vehicle, never an upstream NIO endpoint."""

    def __init__(
        self, session: ClientSession, *, api_origin: str, credential: str
    ) -> None:
        origin = urlsplit(api_origin)
        if (
            origin.scheme != "https"
            or not origin.hostname
            or origin.username is not None
            or origin.password is not None
            or origin.path not in ("", "/")
            or origin.query
            or origin.fragment
        ):
            raise ValueError("Invalid Companion API origin")
        if not _CREDENTIAL.fullmatch(credential):
            raise ValueError("Invalid Companion consumer credential")
        self._session = session
        self._url = api_origin.rstrip("/") + _PATH
        self._credential = credential

    async def async_fetch(
        self, *, expected_vin: str, expected_vehicle_key: str | None = None
    ) -> CompanionSnapshot:
        """Allow one bounded retry for the owner's shared cache-read admission."""
        for attempt in range(2):
            try:
                return await self._async_fetch_once(
                    expected_vin=expected_vin, expected_vehicle_key=expected_vehicle_key
                )
            except CompanionFetchError as err:
                if (
                    attempt
                    or err.status != 429
                    or err.retry_after is None
                    or err.retry_after > 5
                ):
                    raise
                await asyncio.sleep(err.retry_after)
        raise AssertionError("Unreachable")

    async def _async_fetch_once(
        self, *, expected_vin: str, expected_vehicle_key: str | None = None
    ) -> CompanionSnapshot:
        """Fetch and validate without logging response data or credentials."""
        expected_vin = normalize_vin(expected_vin)
        started = monotonic()
        try:
            async with self._session.get(
                self._url,
                headers={
                    "Authorization": f"Bearer {self._credential}",
                    "Accept": "application/json",
                },
                allow_redirects=False,
                timeout=ClientTimeout(total=10),
            ) as response:
                status = response.status
                retry_after = response.headers.get("Retry-After")
                body = bytearray()
                while len(body) <= _MAX_BODY:
                    chunk = await response.content.read(
                        min(8192, _MAX_BODY + 1 - len(body))
                    )
                    if not chunk:
                        break
                    body.extend(chunk)
        except TimeoutError:
            raise CompanionFetchError(
                "retry_later",
                reason="timeout",
                duration_ms=int((monotonic() - started) * 1000),
            ) from None
        except ClientError:
            raise CompanionFetchError(
                "retry_later",
                reason="network",
                duration_ms=int((monotonic() - started) * 1000),
            ) from None
        if len(body) > _MAX_BODY:
            raise CompanionFetchError(
                "invalid_response",
                reason="oversized_body",
                status=status,
                duration_ms=int((monotonic() - started) * 1000),
            )
        try:
            payload = json.loads(body)
        except (UnicodeDecodeError, json.JSONDecodeError):
            raise CompanionFetchError(
                "retry_later" if 500 <= status <= 599 else "invalid_response",
                reason="invalid_http_body" if 500 <= status <= 599 else "invalid_json",
                status=status,
                retry_after=_retry_delay(retry_after) if status >= 500 else None,
                duration_ms=int((monotonic() - started) * 1000),
            ) from None
        if status != 200:
            try:
                kind = classify_companion_error(status, payload)
            except CompanionContractError:
                kind = "retry_later" if 500 <= status <= 599 else "invalid_response"
                raise CompanionFetchError(
                    kind,
                    reason="http_5xx" if 500 <= status <= 599 else "unexpected_http",
                    status=status,
                    retry_after=_retry_delay(retry_after) if status >= 500 else None,
                    duration_ms=int((monotonic() - started) * 1000),
                ) from None
            delay = (
                _retry_delay(retry_after, admission=status == 429)
                if kind == "retry_later"
                else None
            )
            raise CompanionFetchError(
                kind,
                reason=(
                    "rate_limited"
                    if status == 429
                    else "service_unavailable"
                    if status == 503 and kind == "retry_later"
                    else kind
                ),
                status=status,
                retry_after=delay,
                duration_ms=int((monotonic() - started) * 1000),
            )
        try:
            snapshot = parse_companion_snapshot(payload)
        except CompanionContractError:
            raise CompanionFetchError(
                "invalid_response",
                reason="contract",
                status=status,
                duration_ms=int((monotonic() - started) * 1000),
            ) from None
        if snapshot.vin != expected_vin or (
            expected_vehicle_key is not None
            and snapshot.vehicle_key != expected_vehicle_key
        ):
            raise CompanionFetchError(
                "identity_mismatch",
                reason="identity",
                status=status,
                duration_ms=int((monotonic() - started) * 1000),
            )
        return snapshot


async def async_validate_companion_candidate(
    client: CompanionVehicleClient,
    *,
    expected_vin: str,
    required_fields: tuple[str, ...] = ("socPercent", "rangeKm", "odometerKm"),
    expected_vehicle_key: str | None = None,
) -> CompanionCandidate:
    """Preflight a source switch; never commit or unload a config entry.

    The default requirements preserve the owner's current core HA/ledger
    coverage. The proof contract intentionally cannot pass this gate while
    range and odometer units remain unverified.
    """
    snapshot = await client.async_fetch(
        expected_vin=expected_vin, expected_vehicle_key=expected_vehicle_key
    )
    now = datetime.now(UTC)
    if not timedelta(
        seconds=-30
    ) <= now - snapshot.snapshot_at <= MAX_SOURCE_AGE or any(
        not field_is_current(snapshot.fields[name], now) for name in required_fields
    ):
        raise CompanionFetchError("insufficient_coverage")
    return CompanionCandidate(snapshot, required_fields)
