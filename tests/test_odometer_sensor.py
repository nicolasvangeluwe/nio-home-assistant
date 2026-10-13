"""Odometer retention never substitutes unknown or NIO sentinel values."""

from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from custom_components.nio_telematics.models import NioSocStatus, NioVehicleData
from custom_components.nio_telematics.sensor import (
    NioOdometerSensor,
    SENSORS,
    _last_recorded_odometer,
    _odometer_number,
)


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        (6266, 6266.0),
        ("6266", 6266.0),
        ("unknown", None),
        ("unavailable", None),
        (-1, None),
        (0xFFFFFFFF, None),
        (float("inf"), None),
    ],
)
def test_odometer_validation(raw: object, expected: float | None) -> None:
    assert _odometer_number(raw) == expected


def test_recorder_recovery_skips_newer_unknown() -> None:
    earlier = datetime(2026, 10, 13, 18, 0, tzinfo=UTC)
    states = [
        SimpleNamespace(
            state="6266",
            attributes={"source_sample": "2026-10-13T17:58:00+00:00"},
            last_changed=earlier,
        ),
        SimpleNamespace(state="unknown", attributes={}, last_changed=earlier),
    ]
    assert _last_recorded_odometer(states) == (
        6266.0,
        "2026-10-13T17:58:00+00:00",
    )


def test_restored_odometer_exposes_age_until_real_mileage_returns() -> None:
    coordinator = MagicMock()
    coordinator.config_entry.data = {"vin": "LJNABC12345678901"}
    coordinator.data = NioVehicleData(
        vin="LJNABC12345678901",
        soc_status=NioSocStatus(None, None, None, None, None, None, None),
        fetched_at=datetime.now(UTC),
        telemetry={"vehicle_status": {"vehl_state": "locked"}},
        endpoint_status={"vehicle_status": "success"},
    )
    description = next(item for item in SENSORS if item.key == "odometer")
    sensor = NioOdometerSensor(coordinator, description)
    sensor._restored_odometer = 6266
    sensor._restored_sample_time = "2026-10-13T17:58:00+00:00"
    assert sensor.native_value == 6266
    assert sensor.extra_state_attributes["data_retained"] is True
    assert sensor.extra_state_attributes["source_sample"] == (
        "2026-10-13T17:58:00+00:00"
    )
