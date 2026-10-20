"""Isolated parser for the proposed Companion cached-vehicle contract.

Not imported by the live config flow or coordinator. A supported connection
method needs a real backend, credential lifecycle and migration tests first.
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from .models import normalize_vin

_UTC_MILLIS = re.compile(r"^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d\.\d{3}Z$")
_VEHICLE_KEY = re.compile(r"^[a-f0-9]{64}$")
_ENERGY_STATES = frozenset(
    {"NO_CHARGING", "CHARGE_PROCESSING", "CHARGE_COMPLETE", "CHARGE_FAULT"}
)
_DYNAMICS_STATES = frozenset(
    {
        "PARKING_CHARGING",
        "DRIVING_CHARGING",
        "NOT_CHARGING",
        "CHARGE_COMPLETE",
        "CHARGING_EXCEPTION",
        "CHARGING_INVALID",
    }
)
_VEHICLE_STATES = frozenset(
    {"DRIVING", "PARKED_VEHICLE", "DRIVER_PRESENT", "SW_UPDATE", "EXCEPTION", "INVALID"}
)

# (unit, allowed endpoints, numeric bounds or exact enum). Keep in step with
# the backend's version-1 allowlist; adding fields requires a version review.
_FIELDS: dict[
    str, tuple[str | None, frozenset[str], tuple[int, int] | frozenset[str]]
] = {
    "socPercent": ("%", frozenset({"soc_status"}), (0, 100)),
    "targetSocPercent": ("%", frozenset({"soc_status"}), (0, 100)),
    "maximumSocPercent": ("%", frozenset({"soc_status"}), (80, 100)),
    "batteryCurrentA": ("A", frozenset({"soc_status"}), (-200, 200)),
    "vehicleState": (None, frozenset({"vehicle_status"}), _VEHICLE_STATES),
    "energyChargingState": (None, frozenset({"soc_status"}), _ENERGY_STATES),
    "dynamicsChargingState": (
        None,
        frozenset({"vehicle_status"}),
        _DYNAMICS_STATES,
    ),
    "rangeKm": ("km", frozenset({"soc_status"}), (0, 999999)),
    "odometerKm": ("km", frozenset({"vehicle_status"}), (0, 9999999)),
}
_REASONS = frozenset({"not_reported", "unit_unverified", "conflicting_same_time"})


class CompanionContractError(ValueError):
    """A malformed response; never include private payload data in the error."""


def _invalid() -> CompanionContractError:
    return CompanionContractError("Invalid Companion vehicle contract")


def _timestamp(value: Any) -> datetime:
    if not isinstance(value, str) or not _UTC_MILLIS.fullmatch(value):
        raise _invalid()
    try:
        result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        raise _invalid() from None
    if result.astimezone(UTC).isoformat(timespec="milliseconds") != value.replace(
        "Z", "+00:00"
    ):
        raise _invalid()
    return result


@dataclass(frozen=True, slots=True)
class CompanionField:
    """One provider-sourced field, retaining its own freshness and provenance."""

    value: float | str | None
    unit: str | None
    source_timestamp: datetime | None
    received_at: datetime | None
    quality: str
    reason: str | None
    source_endpoint: str | None

    @property
    def usable(self) -> bool:
        """Only a current, verified value can feed a native HA entity."""
        return self.quality == "valid" and self.value is not None


@dataclass(frozen=True, slots=True)
class CompanionSnapshot:
    """Validated response, not yet an active NIO coordinator snapshot."""

    vehicle_key: str
    vin: str
    source_generation: int
    snapshot_at: datetime
    fields: dict[str, CompanionField]

    def usable_value(self, key: str) -> float | str | None:
        """Withhold unverified or stale data; no source is made fresh by parsing."""
        field = self.fields[key]
        return field.value if field.usable else None


def parse_companion_snapshot(
    payload: Any, *, allow_synthetic: bool = False
) -> CompanionSnapshot:
    """Validate version 1 without emitting credentials, VINs or payload text."""
    if not isinstance(payload, dict) or type(payload.get("schemaVersion")) is not int:
        raise _invalid()
    if payload["schemaVersion"] != 1 or payload.get("source") != "nio_official":
        raise _invalid()
    key = payload.get("vehicleKey")
    if not isinstance(key, str) or not _VEHICLE_KEY.fullmatch(key):
        raise _invalid()
    identity = payload.get("identity")
    if not isinstance(identity, dict) or identity.get("ownership") != "verified":
        raise _invalid()
    try:
        vin = normalize_vin(identity["vin"])
    except (KeyError, AttributeError, TypeError, ValueError):
        raise _invalid() from None
    if vin != identity["vin"]:
        raise _invalid()
    synthetic = payload.get("synthetic")
    if type(synthetic) is not bool or (synthetic and not allow_synthetic):
        raise _invalid()
    generation = payload.get("sourceGeneration")
    if type(generation) is not int or generation < 1:
        raise _invalid()
    capabilities = payload.get("capabilities")
    if capabilities != {
        "readOnly": True,
        "location": False,
        "controls": False,
        "history": False,
    }:
        raise _invalid()
    snapshot_at = _timestamp(payload.get("snapshotAt"))
    raw_fields = payload.get("fields")
    if not isinstance(raw_fields, dict) or raw_fields.keys() != _FIELDS.keys():
        raise _invalid()
    fields: dict[str, CompanionField] = {}
    for name, (unit, endpoints, allowed) in _FIELDS.items():
        raw = raw_fields[name]
        if not isinstance(raw, dict) or raw.get("unit") != unit:
            raise _invalid()
        quality = raw.get("quality")
        reason = raw.get("reason")
        value = raw.get("value")
        source = raw.get("sourceTimestamp")
        received = raw.get("receivedAt")
        endpoint = raw.get("sourceEndpoint")
        if quality not in {"valid", "stale", "future_clock", "unavailable"}:
            raise _invalid()
        if reason is not None and reason not in _REASONS:
            raise _invalid()
        if (source is None) != (received is None) or (
            (source is None) != (endpoint is None)
        ):
            raise _invalid()
        if endpoint is not None and endpoint not in endpoints:
            raise _invalid()
        source_time = _timestamp(source) if source is not None else None
        received_time = _timestamp(received) if received is not None else None
        if received_time is not None and received_time > snapshot_at:
            raise _invalid()
        if quality in {"valid", "stale"}:
            if value is None or reason is not None or source_time is None:
                raise _invalid()
            if (
                received_time is None
                or source_time > received_time
                or source_time > snapshot_at
            ):
                raise _invalid()
            if isinstance(allowed, tuple):
                if type(value) not in (int, float) or not math.isfinite(value):
                    raise _invalid()
                if not allowed[0] <= value <= allowed[1]:
                    raise _invalid()
                value = float(value)
            elif not isinstance(value, str) or value not in allowed:
                raise _invalid()
        elif value is not None:
            raise _invalid()
        elif quality == "future_clock":
            if reason is not None or source_time is None:
                raise _invalid()
        elif reason is None or (reason == "unit_unverified") != (
            source_time is not None
        ):
            raise _invalid()
        if name in {"rangeKm", "odometerKm"} and (
            value is not None
            or reason
            not in {"not_reported", "unit_unverified", "conflicting_same_time"}
        ):
            raise _invalid()
        fields[name] = CompanionField(
            value, unit, source_time, received_time, quality, reason, endpoint
        )
    return CompanionSnapshot(key, vin, generation, snapshot_at, fields)


def classify_companion_error(status: int, payload: Any) -> str:
    """Keep consumer-auth failure distinct from upstream source failure."""
    code = payload.get("error") if isinstance(payload, dict) else None
    match status, code:
        case 401, "unauthorized":
            return "consumer_reauthentication_required"
        case 429, "rate_limited":
            return "retry_later"
        case 503, "source_reauthorization_required":
            return "upstream_reauthorization_required"
        case 503, "source_disconnected":
            return "source_disconnected"
        case 503, "unavailable":
            return "retry_later"
        case _:
            raise _invalid()
