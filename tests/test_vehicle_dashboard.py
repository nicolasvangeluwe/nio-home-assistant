"""Dashboard preferences remain optional, per car and free of secrets."""

from unittest.mock import patch

from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.nio_telematics.const import DOMAIN
from custom_components.nio_telematics.vehicle_dashboard import (
    PREFERENCES_SCHEMA,
    _vehicle,
    preferences_for_entry,
)


def test_dashboard_defaults_do_not_require_evcc() -> None:
    preferences = PREFERENCES_SCHEMA({})
    assert preferences["language"] == "auto"
    assert preferences["model"] == "auto"
    assert preferences["evcc_history"] == ""
    assert preferences["battery_capacity_kwh"] is None


def test_existing_ledger_is_not_silently_disabled(hass: HomeAssistant) -> None:
    entry = MockConfigEntry(
        domain=DOMAIN, title="Test car", data={"vin": "HJNNBDLH3SB701418"}
    )
    entry.add_to_hass(hass)
    hass.data["nio_telematics_car_dashboard"] = {
        "settings": {
            entry.entry_id: {
                "capacity_kwh": 90,
                "full_range_km": 557,
                "home_connected": "binary_sensor.evcc_connected",
            }
        },
        "recorders": {},
    }
    preferences = preferences_for_entry(hass, entry)
    assert preferences["ledger_enabled"] is True
    assert preferences["battery_capacity_kwh"] == 90
    assert preferences["full_range_km"] == 557


async def test_options_flow_preserves_unrelated_options(hass: HomeAssistant) -> None:
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Test car",
        data={"vin": "HJNNBDLH3SB701418"},
        options={"unrelated": {"keep": True}},
    )
    entry.add_to_hass(hass)
    form = await hass.config_entries.options.async_init(entry.entry_id)
    assert form["type"] is FlowResultType.FORM
    result = await hass.config_entries.options.async_configure(
        form["flow_id"],
        user_input={"model": "ET5 Touring", "language": "nl"},
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["data"]["unrelated"] == {"keep": True}
    assert result["data"]["vehicle_dashboard"]["model"] == "ET5 Touring"


async def test_history_requires_calibration_in_options_flow(
    hass: HomeAssistant,
) -> None:
    entry = MockConfigEntry(
        domain=DOMAIN, title="Test car", data={"vin": "HJNNBDLH3SB701418"}
    )
    entry.add_to_hass(hass)
    form = await hass.config_entries.options.async_init(entry.entry_id)
    result = await hass.config_entries.options.async_configure(
        form["flow_id"], user_input={"ledger_enabled": True}
    )
    assert result["type"] is FlowResultType.FORM
    assert result["errors"]["base"] == "ledger_calibration_required"


def test_vehicle_metadata_uses_stable_registry_ids_without_vin(
    hass: HomeAssistant,
) -> None:
    entry = MockConfigEntry(
        domain=DOMAIN, title="Test car", data={"vin": "HJNNBDLH3SB701418"}
    )
    entry.add_to_hass(hass)
    registry_entry = type(
        "Entry",
        (),
        {
            "unique_id": "HJNNBDLH3SB701418_battery_state_of_charge",
            "entity_id": "sensor.my_renamed_nio_soc",
        },
    )()
    with patch(
        "custom_components.nio_telematics.vehicle_dashboard.er.async_entries_for_config_entry",
        return_value=[registry_entry],
    ):
        result = _vehicle(hass, entry, {})
    assert result["entities"]["battery_state_of_charge"] == "sensor.my_renamed_nio_soc"
    assert "vin" not in result
    assert "HJNNBDLH3SB701418" not in str(result)
