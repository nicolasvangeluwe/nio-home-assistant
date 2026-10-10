"""Additional documented SoC-status fields."""

from datetime import UTC, datetime

import pytest

from custom_components.nio_telematics.models import NioSocStatus, NioVehicleData
from custom_components.nio_telematics.sensor import SENSORS


@pytest.mark.parametrize(
    ("raw", "expected"), [(61, 21), (0, None), (254, None), (255, None)]
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


@pytest.mark.parametrize(
    ("packs", "voltage", "current"),
    [
        ([{"btry_pak_voltage": 359, "btry_pak_curnt": 0}], 359, 0),
        ([{"btry_pak_voltage": "388.3", "btry_pak_curnt": "-2.5"}], 388.3, -2.5),
        ([], None, None),
        (
            [
                {"btry_pak_voltage": 359, "btry_pak_curnt": 0},
                {"btry_pak_voltage": 360, "btry_pak_curnt": 1},
            ],
            None,
            None,
        ),
        ([{"btry_pak_voltage": float("nan"), "btry_pak_curnt": True}], None, None),
    ],
)
def test_single_pack_electrical_sensors(packs, voltage, current) -> None:
    data = NioVehicleData(
        vin="LJNABC12345678901",
        soc_status=NioSocStatus(None, None, None, None, None, None, None),
        fetched_at=datetime.now(UTC),
        telemetry={"soc_status": {"btry_paks": packs}},
        endpoint_status={"soc_status": "success"},
    )
    descriptions = {sensor.key: sensor for sensor in SENSORS}
    assert descriptions["battery_pack_voltage"].value_fn(data) == voltage
    assert descriptions["battery_pack_current"].value_fn(data) == current


def test_pack_count_diagnostics_and_default_visibility() -> None:
    data = NioVehicleData(
        vin="LJNABC12345678901",
        soc_status=NioSocStatus(None, None, None, None, None, None, None),
        fetched_at=datetime.now(UTC),
        telemetry={
            "soc_status": {
                "btry_paks": [
                    {
                        "btry_pak_voltage": 359,
                        "btry_pak_curnt": 0,
                        "sin_btry_qunty_of_pak": 96,
                        "temp_prb_qunty": 48,
                    }
                ]
            }
        },
        endpoint_status={"soc_status": "success"},
    )
    descriptions = {sensor.key: sensor for sensor in SENSORS}
    assert descriptions["battery_pack_cell_count"].value_fn(data) == 96
    assert descriptions["battery_pack_temperature_probe_count"].value_fn(data) == 48
    assert descriptions["battery_pack_voltage"].entity_registry_enabled_default
    assert descriptions["battery_pack_current"].entity_registry_enabled_default
    assert descriptions["battery_pack_count"].entity_registry_enabled_default
