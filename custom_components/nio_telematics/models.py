"""Typed NIO Open Telematics data models."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
import re
from typing import Any

_VIN_PATTERN = re.compile(r"^[A-HJ-NPR-Z0-9]{17}$")


def normalize_vin(value: str) -> str:
    """Normalize and validate a standard 17-character VIN."""
    vin = value.strip().upper()
    if not _VIN_PATTERN.fullmatch(vin):
        raise ValueError("VIN must contain 17 valid characters")
    return vin


def _optional_float(value: Any) -> float | None:
    if value is None or isinstance(value, bool):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _optional_str(value: Any) -> str | None:
    if isinstance(value, str):
        return value or None
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return str(value)
    return None


def _event_datetime(value: Any) -> datetime | None:
    timestamp = _optional_float(value)
    if timestamp is None:
        return None
    # Accept seconds and milliseconds without guessing beyond those formats.
    if timestamp > 10_000_000_000:
        timestamp /= 1000
    try:
        return datetime.fromtimestamp(timestamp, tz=UTC)
    except (OSError, OverflowError, ValueError):
        return None


@dataclass(frozen=True, slots=True)
class NioSocStatus:
    """Latest verified fields from a NIO SoC status record."""

    soc: float | None
    remaining_range: float | None
    charging_state: str | None
    charging_target: float | None
    maximum_soc: float | None
    high_voltage_battery_current: float | None
    event_time: datetime | None

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> NioSocStatus:
        """Parse only fields verified in the official SoC schema."""
        return cls(
            soc=_optional_float(payload.get("soc")),
            remaining_range=_optional_float(payload.get("remaining_range")),
            charging_state=_optional_str(payload.get("chrg_state")),
            charging_target=_optional_float(payload.get("chrg_final_soc")),
            maximum_soc=_optional_float(payload.get("max_soc")),
            high_voltage_battery_current=_optional_float(
                payload.get("hivolt_btry_curnt")
            ),
            event_time=_event_datetime(payload.get("sample_timestamp")),
        )

    @classmethod
    def merge(cls, *statuses: NioSocStatus) -> NioSocStatus:
        """Merge snapshots in priority order, keeping the newest timestamp."""

        def first(attribute: str) -> Any:
            return next(
                (
                    value
                    for status in statuses
                    if (value := getattr(status, attribute)) is not None
                ),
                None,
            )

        event_times = [status.event_time for status in statuses if status.event_time]
        return cls(
            soc=first("soc"),
            remaining_range=first("remaining_range"),
            charging_state=first("charging_state"),
            charging_target=first("charging_target"),
            maximum_soc=first("maximum_soc"),
            high_voltage_battery_current=first("high_voltage_battery_current"),
            event_time=max(event_times) if event_times else None,
        )


@dataclass(frozen=True, slots=True)
class NioVehicleData:
    """Coordinator snapshot for one vehicle."""

    vin: str
    soc_status: NioSocStatus
    fetched_at: datetime
