"""Dashboard preferences remain optional, per car and free of secrets."""

import asyncio
import hashlib
import inspect
import json
from datetime import UTC, datetime
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock, patch

from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from homeassistant.helpers.storage import Store
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.nio_telematics.car_dashboard.coordinator import (
    _is_connected,
    _source_time,
)
from custom_components.nio_telematics.const import DOMAIN
from custom_components.nio_telematics.artwork import (
    PAINTS_BY_MODEL,
    pin_model_for_paint,
    valid_paint,
)
from custom_components.nio_telematics.vehicle_dashboard import (
    PREFERENCES_SCHEMA,
    _check_import_preferences,
    _vehicle,
    async_reconcile_ledger,
    preferences_for_entry,
    websocket_backup,
)


def test_dashboard_bundles_local_vehicle_artwork() -> None:
    assets = Path(__file__).resolve().parents[1] / "custom_components/nio_telematics"
    artwork = (assets / "et5-touring-studio.png").read_bytes()
    assert artwork.startswith(b"\x89PNG\r\n\x1a\n")
    source = (assets / "nio-vehicle-card.js").read_text(encoding="utf-8")
    assert "nio-vehicle-dashboard" in source
    assert "/nio_telematics/et5-touring-studio.png" in source


def test_model_paint_catalogue_is_complete_and_local() -> None:
    root = Path(__file__).resolve().parents[1] / "custom_components/nio_telematics/artwork"
    catalogue = json.loads((root / "catalogue.json").read_text(encoding="utf-8"))
    assert catalogue["schema_version"] == 1
    assert len(catalogue["models"]) == 7
    assert sum(len(model["paints"]) for model in catalogue["models"]) == 51
    names = {"et5": "ET5", "et5-touring": "ET5 Touring", "el6": "EL6", "et7": "ET7", "el7": "EL7", "el8": "EL8", "es8": "ES8"}
    for model in catalogue["models"]:
        name = names[model["id"]]
        assert model["default_paint"] in PAINTS_BY_MODEL[name]
        for paint in model["paints"]:
            assert paint["id"] in PAINTS_BY_MODEL[name]
            assert paint["file"].startswith(f'{model["id"]}/')
            path = root / paint["file"]
            assert path.is_file()
            assert hashlib.sha256(path.read_bytes()).hexdigest() == paint["sha256"]


def test_paint_selection_stays_with_its_car_model(hass: HomeAssistant) -> None:
    assert valid_paint("auto", "auto", "My ET5 Touring")
    assert valid_paint("ET5 Touring", "auto", "Any car")
    touring_paint = "sunlight-gold"
    assert valid_paint("ET5 Touring", touring_paint, "Any car")
    assert valid_paint("auto", touring_paint, "My ET5 Touring")
    assert not valid_paint("ET7", touring_paint, "Any car")
    entry = MockConfigEntry(domain=DOMAIN, title="My ET7", data={"vin": "test"})
    entry.add_to_hass(hass)
    try:
        _check_import_preferences(hass, entry, {"model": "ET7", "paint": touring_paint})
    except ValueError as error:
        assert "paint" in str(error)
    else:
        raise AssertionError("Cross-model paint must be rejected during backup import")


def test_explicit_paint_survives_entry_rename_and_backup(hass: HomeAssistant) -> None:
    entry = MockConfigEntry(domain=DOMAIN, title="My ET5 Touring", data={"vin": "test"})
    entry.add_to_hass(hass)
    selected = pin_model_for_paint(
        PREFERENCES_SCHEMA({"model": "auto", "paint": "sunlight-gold"}), entry.title
    )
    assert selected["model"] == "ET5 Touring"
    hass.config_entries.async_update_entry(entry, title="My car")
    assert valid_paint(selected["model"], selected["paint"], entry.title)
    restored = _check_import_preferences(hass, entry, selected)
    assert restored["model"] == "ET5 Touring"
    assert restored["paint"] == "sunlight-gold"


def test_dashboard_defaults_do_not_require_evcc() -> None:
    preferences = PREFERENCES_SCHEMA({})
    assert preferences["language"] == "auto"
    assert preferences["model"] == "auto"
    assert preferences["paint"] == "auto"
    assert preferences["evcc_history"] == ""
    assert preferences["battery_capacity_kwh"] is None
    assert all(
        preferences[key] == ""
        for key in (
            "soc_entity",
            "range_entity",
            "odometer_entity",
            "charging_state_entity",
            "charge_limit_entity",
        )
    )


def test_user_selected_sources_use_ha_report_time_when_no_nio_timestamp() -> None:
    reported = datetime(2026, 10, 13, 12, 0, tzinfo=UTC)
    state = SimpleNamespace(
        attributes={}, last_reported=reported, last_updated=reported
    )
    assert _source_time(state, "last_valid_sample") == reported.timestamp()
    assert _is_connected(SimpleNamespace(state="connected"))
    assert not _is_connected(SimpleNamespace(state="disconnected"))


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
                "cost_sources": {
                    "energy": "sensor.charge_energy",
                    "solar": "sensor.solar_energy",
                    "total_cost": "sensor.charge_cost",
                    "grid_price": "sensor.grid_price",
                    "export_price": "sensor.export_price",
                },
            }
        },
        "recorders": {},
    }
    preferences = preferences_for_entry(hass, entry)
    assert preferences["ledger_enabled"] is True
    assert preferences["battery_capacity_kwh"] == 90
    assert preferences["full_range_km"] == 557
    assert preferences["cost_energy"] == "sensor.charge_energy"
    assert preferences["cost_export_price"] == "sensor.export_price"


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


async def test_options_flow_rejects_colour_from_another_model(
    hass: HomeAssistant,
) -> None:
    entry = MockConfigEntry(domain=DOMAIN, title="My ET5 Touring", data={"vin": "test"})
    entry.add_to_hass(hass)
    form = await hass.config_entries.options.async_init(entry.entry_id)
    result = await hass.config_entries.options.async_configure(
        form["flow_id"], user_input={"model": "ET7", "paint": "sunlight-gold"}
    )
    assert result["type"] is FlowResultType.FORM
    assert result["errors"]["base"] == "invalid_paint_for_model"
    assert entry.options.get("vehicle_dashboard") is None


async def test_options_flow_pins_auto_model_when_paint_is_chosen(
    hass: HomeAssistant,
) -> None:
    entry = MockConfigEntry(domain=DOMAIN, title="My ET5 Touring", data={"vin": "test"})
    entry.add_to_hass(hass)
    form = await hass.config_entries.options.async_init(entry.entry_id)
    result = await hass.config_entries.options.async_configure(
        form["flow_id"], user_input={"model": "auto", "paint": "sunlight-gold"}
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    saved = result["data"]["vehicle_dashboard"]
    assert saved["model"] == "ET5 Touring"
    hass.config_entries.async_update_entry(entry, title="My car")
    assert _check_import_preferences(hass, entry, saved)["paint"] == "sunlight-gold"


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


def test_vehicle_sources_can_override_native_entities_without_losing_defaults(
    hass: HomeAssistant,
) -> None:
    entry = MockConfigEntry(
        domain=DOMAIN, title="Test car", data={"vin": "HJNNBDLH3SB701418"}
    )
    entry.add_to_hass(hass)
    native = type(
        "Entry",
        (),
        {
            "unique_id": "HJNNBDLH3SB701418_battery_state_of_charge",
            "entity_id": "sensor.nio_soc",
        },
    )()
    with patch(
        "custom_components.nio_telematics.vehicle_dashboard.er.async_entries_for_config_entry",
        return_value=[native],
    ):
        result = _vehicle(
            hass,
            entry,
            {"soc_entity": "sensor.chosen_soc", "evcc_power": "sensor.charger_power"},
        )
    assert result["entities"]["battery_state_of_charge"] == "sensor.chosen_soc"
    assert result["native_entities"]["battery_state_of_charge"] == "sensor.nio_soc"
    assert result["preferences"]["evcc_power"] == "sensor.charger_power"


async def test_selected_sources_reach_optional_ledger(hass: HomeAssistant) -> None:
    costs = {
        "energy": "sensor.cost_energy",
        "solar": "sensor.cost_solar",
        "total_cost": "sensor.cost_total",
        "grid_price": "sensor.grid_rate",
        "export_price": "sensor.export_rate",
    }
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Test car",
        data={"vin": "HJNNBDLH3SB701418"},
        options={
            "vehicle_dashboard": {
                "ledger_enabled": True,
                "battery_capacity_kwh": 90,
                "full_range_km": 557,
                "soc_entity": "sensor.chosen_soc",
                "range_entity": "sensor.chosen_range",
                "odometer_entity": "sensor.chosen_odometer",
                "evcc_connected": "binary_sensor.charger_connected",
                "evcc_history": "sensor.evcc_sessions",
                **{f"cost_{key}": value for key, value in costs.items()},
            }
        },
    )
    entry.add_to_hass(hass)
    hass.data["nio_telematics_car_dashboard"] = {"recorders": {}, "settings": {}}
    configure = AsyncMock()
    with (
        patch(
            "custom_components.nio_telematics.vehicle_dashboard.er.async_entries_for_config_entry",
            return_value=[],
        ),
        patch(
            "custom_components.nio_telematics.vehicle_dashboard.async_configure_recorder",
            configure,
        ),
    ):
        await async_reconcile_ledger(hass, entry)
    settings = configure.await_args.args[2]
    assert settings["soc"] == "sensor.chosen_soc"
    assert settings["range"] == "sensor.chosen_range"
    assert settings["odometer"] == "sensor.chosen_odometer"
    assert settings["home_connected"] == "binary_sensor.charger_connected"
    assert settings["cost_sources"] == costs


async def test_dashboard_backup_preview_and_restore_preserve_vehicle_identity(
    hass: HomeAssistant,
) -> None:
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Test car",
        data={"vin": "HJNNBDLH3SB701418"},
        options={"unrelated": {"keep": True}, "vehicle_dashboard": {"language": "nl"}},
    )
    entry.add_to_hass(hass)
    settings_store = Store(hass, 1, "nio_telematics.car_dashboard_settings")
    hass.data["nio_telematics_car_dashboard"] = {
        "recorders": {},
        "settings": {},
        "store": settings_store,
        "lock": asyncio.Lock(),
    }
    history_store = Store(hass, 1, f"nio_car_dashboard.{entry.entry_id}")
    original = {
        "trips": [],
        "charges": {},
        "samples": [],
        "counters": [],
        "parked_losses": [],
        "source_transitions": [],
        "native_replays": {},
        "last": None,
        "active": None,
        "opening": None,
        "preferences": {},
        "revision": 3,
    }
    await history_store.async_save(original)
    connection = SimpleNamespace(
        user=SimpleNamespace(is_admin=True), send_result=Mock(), send_error=Mock()
    )

    async def call_backup(message):
        result = websocket_backup(hass, connection, message)
        if inspect.isawaitable(result):
            await result
        await hass.async_block_till_done()

    await call_backup(
        {"id": 1, "entry_id": entry.entry_id, "action": "export"},
    )
    backup = connection.send_result.call_args.args[1]
    assert "vin" not in backup
    assert backup["history"]["revision"] == 3

    backup["preferences"]["language"] = "en"
    backup["history"]["revision"] = 4
    await call_backup(
        {"id": 2, "entry_id": entry.entry_id, "action": "preview", "backup": backup},
    )
    preview = connection.send_result.call_args.args[1]
    assert preview["current"]["revision"] == 3
    assert (await history_store.async_load())["revision"] == 3

    await call_backup(
        {
            "id": 3,
            "entry_id": entry.entry_id,
            "action": "restore",
            "backup": backup,
            "expected_revision": 3,
            "confirmation": "RESTORE",
        },
    )
    assert not connection.send_error.called, connection.send_error.call_args_list
    assert entry.options["unrelated"] == {"keep": True}
    assert entry.options["vehicle_dashboard"]["language"] == "en"
    restored_store = Store(hass, 1, f"nio_car_dashboard.{entry.entry_id}")
    assert (await restored_store.async_load())["revision"] == 4
