"""Tests for selected numeric telemetry conversions."""

from datetime import UTC, datetime

from custom_components.nio_telematics.models import NioSocStatus, NioVehicleData
from custom_components.nio_telematics.sensor import SENSORS


def _data(endpoint: str, field: str, value: object) -> NioVehicleData:
    return NioVehicleData(
        vin="LJNABC12345678901",
        soc_status=NioSocStatus(None, None, None, None, None, None, None),
        fetched_at=datetime.now(UTC),
        telemetry={endpoint: {field: value}},
        endpoint_status={endpoint: "success"},
    )


def test_invalid_vehicle_odometer_and_speed_sentinels() -> None:
    descriptions = {sensor.key: sensor for sensor in SENSORS}
    assert (
        descriptions["odometer"].value_fn(
            _data("vehicle_status", "mileage", 0xFFFFFFFF)
        )
        is None
    )
    assert (
        descriptions["speed"].value_fn(_data("vehicle_status", "speed", 0xFFFF)) is None
    )
    assert (
        descriptions["odometer"].value_fn(_data("vehicle_status", "mileage", 5926))
        == 5926
    )


def test_cell_voltage_is_already_volts_in_reported_response() -> None:
    descriptions = {sensor.key: sensor for sensor in SENSORS}
    high = descriptions["highest_cell_voltage"]
    assert high.value_fn(_data("extremum_data", "sin_btry_hist_volt", 3.75)) == 3.75
    assert high.suggested_display_precision == 3
    assert high.value_fn(_data("extremum_data", "sin_btry_hist_volt", 0xFFFF)) is None
