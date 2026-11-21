"""Exercise real HA flow persistence and scheduling for issue #21."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from homeassistant import config_entries
from homeassistant.config_entries import ConfigEntryState
from homeassistant.data_entry_flow import FlowResultType
from homeassistant.helpers import config_validation as cv
from pytest_homeassistant_custom_component.common import MockConfigEntry
from voluptuous_serialize import convert

from custom_components.nio_telematics import async_setup_entry
from custom_components.nio_telematics.config_flow import NioConfigFlow
from custom_components.nio_telematics.const import DOMAIN, OAUTH_SCOPE_REVISION
from custom_components.nio_telematics.vehicle_dashboard import OPTIONS_KEY


async def loaded_entry(hass):
    """Run real integration setup while replacing network and platform IO only."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="ET5 Touring",
        unique_id="LJNABC12345678901",
        data={
            "vin": "LJNABC12345678901",
            "vehicle_name": "ET5 Touring",
            "connection_method": "direct",
            "scope_revision": OAUTH_SCOPE_REVISION,
            "auth_implementation": "fixture-client",
            "token": {"access_token": "old-fixture"},
        },
        options={"unrelated": {"keep": True}},
    )
    entry.add_to_hass(hass)
    coordinator = MagicMock()
    coordinator.async_config_entry_first_refresh = AsyncMock()
    with (
        patch(
            "custom_components.nio_telematics._async_direct_coordinator",
            AsyncMock(return_value=coordinator),
        ),
        patch.object(hass.config_entries, "async_forward_entry_setups", AsyncMock()),
        patch("custom_components.nio_telematics.async_reconcile_ledger", AsyncMock()),
    ):
        assert await async_setup_entry(hass, entry)
    controller = coordinator.polling_controller
    controller.async_update_options = AsyncMock(wraps=controller.async_update_options)
    entry._async_set_state(hass, ConfigEntryState.LOADED, None)
    return entry, coordinator


@pytest.mark.parametrize("history_error", [None, "fixture history unavailable"])
async def test_options_manager_persists_and_applies_without_reload(hass, history_error):
    """Use HA's options entrypoint and preserve telemetry even on ledger errors."""
    entry, coordinator = await loaded_entry(hass)
    assert not entry.update_listeners
    seen = []

    async def reconcile(hass_arg, saved_entry):
        assert hass_arg is hass
        seen.append(dict(saved_entry.options))
        if history_error:
            raise ValueError(history_error)

    with (
        patch(
            "custom_components.nio_telematics.async_reconcile_ledger",
            side_effect=reconcile,
        ) as apply,
        patch.object(hass.config_entries, "async_schedule_reload") as schedule,
        patch.object(hass.config_entries, "async_reload", AsyncMock()) as reload,
    ):
        form = await hass.config_entries.options.async_init(entry.entry_id)
        assert form["type"] is FlowResultType.FORM
        fields = {key.schema for key in form["data_schema"].schema}
        assert {
            "interval_seconds",
            "idle_interval_seconds",
            "adaptive",
            "connected_entity",
            "charging_entity",
            "power_entity",
        } <= fields
        serialized = {
            field["name"]: field
            for field in convert(
                form["data_schema"], custom_serializer=cv.custom_serializer
            )
        }
        for field_name in (
            "connected_entity",
            "charging_entity",
            "power_entity",
            "soc_entity",
        ):
            assert serialized[field_name].get("type") != "constant"
            assert "entity" in serialized[field_name]["selector"]
        # Keep the optional selector's blank branch usable for clearing a value.
        connected_field = next(
            key
            for key in form["data_schema"].schema
            if getattr(key, "schema", None) == "connected_entity"
        )
        assert form["data_schema"].schema[connected_field]("") == ""
        result = await hass.config_entries.options.async_configure(
            form["flow_id"],
            {
                "model": "ET7",
                "language": "en",
                "interval_seconds": 20,
                "idle_interval_seconds": 180,
            },
        )
        await hass.async_block_till_done()
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert entry.options[OPTIONS_KEY]["model"] == "ET7"
    assert entry.options["polling"] == {
        "interval_seconds": 20,
        "idle_interval_seconds": 180,
        "adaptive": False,
        "connected_entity": "",
        "charging_entity": "",
        "power_entity": "",
    }
    assert entry.options["unrelated"] == {"keep": True}
    assert seen == [dict(entry.options)]
    apply.assert_awaited_once()
    coordinator.polling_controller.async_update_options.assert_awaited_once_with()
    schedule.assert_not_called()
    reload.assert_not_awaited()
    assert entry.runtime_data is coordinator
    errors = hass.data["nio_telematics_dashboard_errors"]
    assert errors.get(entry.entry_id) == history_error


async def test_native_options_reject_adaptive_without_independent_sources(hass):
    """The actual options manager returns the targeted polling validation error."""
    entry, _ = await loaded_entry(hass)
    form = await hass.config_entries.options.async_init(entry.entry_id)
    result = await hass.config_entries.options.async_configure(
        form["flow_id"], {"adaptive": True}
    )
    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": "invalid_polling_sources"}
    assert entry.options == {"unrelated": {"keep": True}}


async def test_native_options_clear_optional_power_and_reopen(hass):
    """Selected sources save, optional power clears, and the form reopens cleanly."""
    hass.states.async_set("binary_sensor.charger_connected", "on")
    hass.states.async_set("binary_sensor.charger_charging", "off")
    hass.states.async_set("sensor.charger_power", "0", {"unit_of_measurement": "kW"})
    entry, coordinator = await loaded_entry(hass)

    first = await hass.config_entries.options.async_init(entry.entry_id)
    result = await hass.config_entries.options.async_configure(
        first["flow_id"],
        {
            "model": "ET7",
            "language": "en",
            "interval_seconds": 15,
            "idle_interval_seconds": 120,
            "adaptive": True,
            "connected_entity": "binary_sensor.charger_connected",
            "charging_entity": "binary_sensor.charger_charging",
            "power_entity": "sensor.charger_power",
        },
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert entry.options["polling"]["power_entity"] == "sensor.charger_power"

    second = await hass.config_entries.options.async_init(entry.entry_id)
    result = await hass.config_entries.options.async_configure(
        second["flow_id"],
        {
            "model": "ET7",
            "language": "en",
            "interval_seconds": 15,
            "idle_interval_seconds": 120,
            "adaptive": True,
            "connected_entity": "binary_sensor.charger_connected",
            "charging_entity": "binary_sensor.charger_charging",
            "power_entity": "",
        },
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert entry.options["polling"]["power_entity"] == ""
    assert entry.options["polling"]["connected_entity"] == (
        "binary_sensor.charger_connected"
    )
    assert entry.options["polling"]["charging_entity"] == (
        "binary_sensor.charger_charging"
    )
    assert entry.options[OPTIONS_KEY]["model"] == "ET7"
    assert entry.options["unrelated"] == {"keep": True}

    reopened = await hass.config_entries.options.async_init(entry.entry_id)
    defaults = {
        key.schema: key.default
        for key in reopened["data_schema"].schema
        if hasattr(key, "schema")
    }
    assert defaults["power_entity"]() == ""
    assert defaults["connected_entity"]() == "binary_sensor.charger_connected"
    assert defaults["charging_entity"]() == "binary_sensor.charger_charging"
    assert coordinator.polling_controller.async_update_options.await_count == 2


@pytest.mark.parametrize("cleared_key", ["connected_entity", "charging_entity"])
async def test_native_options_reject_clearing_required_adaptive_source(
    hass, cleared_key
):
    """Invalid optional-source clears leave persisted options intact."""
    hass.states.async_set("binary_sensor.charger_connected", "on")
    hass.states.async_set("binary_sensor.charger_charging", "off")
    entry, _ = await loaded_entry(hass)
    saved_options = {
        **entry.options,
        "polling": {
            "interval_seconds": 15,
            "idle_interval_seconds": 120,
            "adaptive": True,
            "connected_entity": "binary_sensor.charger_connected",
            "charging_entity": "binary_sensor.charger_charging",
            "power_entity": "",
        },
        OPTIONS_KEY: {"model": "ET7", "language": "en"},
    }
    hass.config_entries.async_update_entry(entry, options=saved_options)
    form = await hass.config_entries.options.async_init(entry.entry_id)
    submission = {
        "model": "ET7",
        "language": "en",
        "interval_seconds": 15,
        "idle_interval_seconds": 120,
        "adaptive": True,
        "connected_entity": "binary_sensor.charger_connected",
        "charging_entity": "binary_sensor.charger_charging",
        "power_entity": "",
    }
    submission[cleared_key] = ""
    result = await hass.config_entries.options.async_configure(
        form["flow_id"], submission
    )
    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": "invalid_polling_sources"}
    assert entry.options == saved_options


async def test_dashboard_edit_retains_existing_polling_settings(hass):
    """An edit to dashboard preferences does not reset saved polling controls."""
    entry, _ = await loaded_entry(hass)
    saved_polling = {
        "interval_seconds": 45,
        "idle_interval_seconds": 180,
        "adaptive": False,
        "connected_entity": "binary_sensor.charger_connected",
        "charging_entity": "binary_sensor.charger_charging",
        "power_entity": "",
    }
    hass.config_entries.async_update_entry(
        entry, options={**entry.options, "polling": saved_polling}
    )
    with patch("custom_components.nio_telematics.async_reconcile_ledger", AsyncMock()):
        form = await hass.config_entries.options.async_init(entry.entry_id)
        result = await hass.config_entries.options.async_configure(
            form["flow_id"], {"model": "ET7", "language": "en"}
        )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert entry.options["polling"] == saved_polling
    assert entry.options[OPTIONS_KEY]["model"] == "ET7"


async def test_native_options_enable_adaptive_and_retain_it_on_dashboard_edit(hass):
    """Real form saves enable the controller and later retain its generic inputs."""
    entry, coordinator = await loaded_entry(hass)
    hass.states.async_set("binary_sensor.test_connected", "on")
    hass.states.async_set("binary_sensor.test_charging", "off")
    controller = coordinator.polling_controller
    with (
        patch("custom_components.nio_telematics.async_reconcile_ledger", AsyncMock()),
        patch.object(hass.config_entries, "async_schedule_reload") as schedule,
        patch.object(hass.config_entries, "async_reload", AsyncMock()) as reload,
    ):
        form = await hass.config_entries.options.async_init(entry.entry_id)
        result = await hass.config_entries.options.async_configure(
            form["flow_id"],
            {
                "adaptive": True,
                "interval_seconds": 15.0,
                "idle_interval_seconds": 120.0,
                "connected_entity": "binary_sensor.test_connected",
                "charging_entity": "binary_sensor.test_charging",
                "power_entity": "",
            },
        )
        assert result["type"] is FlowResultType.CREATE_ENTRY
        saved = dict(entry.options["polling"])
        assert saved["adaptive"] is True
        assert saved["interval_seconds"] == 15
        assert controller.mode == "idle"
        controller.async_update_options.assert_awaited_once_with()

        form = await hass.config_entries.options.async_init(entry.entry_id)
        result = await hass.config_entries.options.async_configure(
            form["flow_id"], {"model": "ET7", "language": "en"}
        )
        assert result["type"] is FlowResultType.CREATE_ENTRY
        assert entry.options["polling"] == saved
        assert entry.options[OPTIONS_KEY]["model"] == "ET7"
        assert controller.async_update_options.await_count == 2
        assert controller.mode == "idle"
        schedule.assert_not_called()
        reload.assert_not_awaited()
    await controller.async_stop()


async def test_native_reauth_schedules_one_reload_without_listener_conflict(
    hass, caplog
):
    """Exercise the real reload helper against an entry set up by the integration."""
    entry, _ = await loaded_entry(hass)
    handler = NioConfigFlow()
    handler.hass = hass
    handler.handler = DOMAIN
    handler.context = {
        "source": config_entries.SOURCE_REAUTH,
        "entry_id": entry.entry_id,
    }
    entry_id = entry.entry_id
    options = dict(entry.options)
    with patch.object(hass.config_entries, "async_schedule_reload") as schedule:
        result = await handler.async_oauth_create_entry(
            {
                "auth_implementation": "fixture-client",
                "token": {"access_token": "new-fixture"},
            }
        )
    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "reauth_successful"
    schedule.assert_called_once_with(entry_id)
    assert entry.entry_id == entry_id
    assert entry.data["token"]["access_token"] == "new-fixture"
    assert entry.options == options
    assert not entry.update_listeners
    assert "has an update listener" not in caplog.text
