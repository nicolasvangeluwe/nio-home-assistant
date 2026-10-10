"""Additional documented SoC-status fields."""

from datetime import UTC, datetime

import pytest

from custom_components.nio_telematics.models import NioSocStatus, NioVehicleData
from custom_components.nio_telematics.sensor import SENSORS


@pytest.mark.parametrize(
    ("raw", "expected"), [(61, 21), (0, -40), (254, None), (255, None)]
)
def test_soc_battery_temperature_excludes_sentinels(raw, expected) -> None:
    description = next(
        sensor
        for sensor in SENSORS
        if sensor.key == "soc_highest_battery_temperature"
    )
    data = NioVehicleData(
        vin="LJNABC12345678901",
        soc_status=NioSocStatus(None, None, None, None, None, None, None),
        fetched_at=datetime.now(UTC),
        telemetry={"soc_status": {"sin_btry_hist_temp": raw}},
        endpoint_status={"soc_status": "success"},
    )
    assert description.value_fn(data) == expected
