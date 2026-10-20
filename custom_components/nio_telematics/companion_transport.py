"""Cache-only Companion transport; never obtains a grant or polls NIO."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
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

    def __init__(self, kind: str) -> None:
        self.kind = kind
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
        """Fetch and validate without logging response data or credentials."""
        expected_vin = normalize_vin(expected_vin)
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
                body = await response.content.read(_MAX_BODY + 1)
        except (ClientError, TimeoutError):
            raise CompanionFetchError("retry_later") from None
        if len(body) > _MAX_BODY:
            raise CompanionFetchError("invalid_response")
        try:
            payload = json.loads(body)
        except (UnicodeDecodeError, json.JSONDecodeError):
            raise CompanionFetchError("invalid_response") from None
        if status != 200:
            try:
                kind = classify_companion_error(status, payload)
            except CompanionContractError:
                kind = "retry_later" if 500 <= status <= 599 else "invalid_response"
                raise CompanionFetchError(kind) from None
            raise CompanionFetchError(kind)
        try:
            snapshot = parse_companion_snapshot(payload)
        except CompanionContractError:
            raise CompanionFetchError("invalid_response") from None
        if snapshot.vin != expected_vin or (
            expected_vehicle_key is not None
            and snapshot.vehicle_key != expected_vehicle_key
        ):
            raise CompanionFetchError("identity_mismatch")
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
