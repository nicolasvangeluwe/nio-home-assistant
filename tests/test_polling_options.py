"""Regression checks for native adaptive-polling options and translations."""

import json
from pathlib import Path
from types import SimpleNamespace

from homeassistant.config_entries import ConfigEntryState

from custom_components.nio_telematics.source_switch import async_switch_source

INTEGRATION = Path(__file__).parents[1] / "custom_components" / "nio_telematics"
POLLING_KEYS = {
    "interval_seconds",
    "idle_interval_seconds",
    "adaptive",
    "connected_entity",
    "charging_entity",
    "power_entity",
}


def test_polling_option_copy_is_localized_in_every_catalog() -> None:
    """All shipped native config-flow catalogs contain polling copy and errors."""
    strings = json.loads((INTEGRATION / "strings.json").read_text(encoding="utf-8"))
    expected_data = strings["options"]["step"]["init"]["data"]
    expected_help = strings["options"]["step"]["init"]["data_description"]
    expected_errors = {
        "invalid_polling_interval",
        "invalid_polling_sources",
    }
    catalogs = sorted((INTEGRATION / "translations").glob("*.json"))
    assert len(catalogs) == 14

    for catalog in catalogs:
        translation = json.loads(catalog.read_text(encoding="utf-8"))
        options = translation["options"]
        init = options["step"]["init"]
        assert POLLING_KEYS <= init["data"].keys(), catalog.name
        assert POLLING_KEYS <= init["data_description"].keys(), catalog.name
        assert expected_errors <= options["error"].keys(), catalog.name
        for key in POLLING_KEYS:
            assert init["data"][key]
            assert init["data_description"][key]
        for key in expected_errors:
            assert options["error"][key]
        # English is the native fallback and must match the source catalog exactly.
        if catalog.stem == "en":
            for key in POLLING_KEYS:
                assert init["data"][key] == expected_data[key]
                assert init["data_description"][key] == expected_help[key]


async def test_source_switch_retains_polling_and_dashboard_options() -> None:
    """Changing a vehicle source does not replace its independent options."""
    options = {
        "polling": {
            "interval_seconds": 45,
            "idle_interval_seconds": 180,
            "adaptive": True,
            "connected_entity": "binary_sensor.charger_connected",
            "charging_entity": "binary_sensor.charger_charging",
            "power_entity": "",
        },
        "vehicle_dashboard": {"model": "ET7", "language": "en"},
        "unrelated": {"keep": True},
    }
    entry = SimpleNamespace(
        entry_id="entry",
        data={"connection_method": "direct", "token": {"access_token": "fixture"}},
        options=options,
        state=ConfigEntryState.LOADED,
        disabled_by=None,
    )
    manager = SimpleNamespace()

    async def unload(_entry_id):
        entry.state = ConfigEntryState.NOT_LOADED
        return True

    async def setup(_entry_id):
        entry.state = ConfigEntryState.LOADED
        return True

    def update(target, *, data):
        target.data = data

    manager.async_unload = unload
    manager.async_setup = setup
    manager.async_update_entry = update
    hass = SimpleNamespace(data={}, config_entries=manager)

    await async_switch_source(
        hass,
        entry,
        {"connection_method": "companion", "companion_credential": "fixture"},
    )

    assert entry.options == options
