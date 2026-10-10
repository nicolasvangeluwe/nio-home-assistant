"""Optional, per-vehicle dashboard preferences and entity discovery."""

from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
from pathlib import Path

import voluptuous as vol
from homeassistant.components import frontend, websocket_api
from homeassistant.components.http import StaticPathConfig
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers import entity_registry as er

from .car_dashboard import async_configure_recorder
from .car_dashboard import manager as ledger_manager
from .const import DOMAIN

OPTIONS_KEY = "vehicle_dashboard"
MODELS = ("auto", "ET5", "ET5 Touring", "ET7", "EL6", "EL7", "EL8", "ES8", "other")
LANGUAGES = (
    "auto",
    "en",
    "nl",
    "fr",
    "de",
    "nb",
    "sv",
    "da",
    "cs",
    "el",
    "hu",
    "lb",
    "pl",
    "pt",
    "ro",
)
SENSOR_KEYS = (
    "battery_state_of_charge",
    "remaining_range",
    "odometer",
    "charging_state",
    "maximum_soc",
)
PREFERENCES_SCHEMA = vol.Schema(
    {
        vol.Optional("model", default="auto"): vol.In(MODELS),
        vol.Optional("language", default="auto"): vol.In(LANGUAGES),
        vol.Optional("evcc_connected", default=""): vol.Any("", cv.entity_id),
        vol.Optional("evcc_power", default=""): vol.Any("", cv.entity_id),
        vol.Optional("evcc_history", default=""): vol.Any("", cv.entity_id),
        vol.Optional("electricity_price", default=""): vol.Any("", cv.entity_id),
        vol.Optional("reimbursement_rate", default=""): vol.Any("", cv.entity_id),
        vol.Optional("battery_capacity_kwh", default=None): vol.Any(
            None, vol.All(vol.Coerce(float), vol.Range(min=1, max=300))
        ),
        vol.Optional("full_range_km", default=None): vol.Any(
            None, vol.All(vol.Coerce(float), vol.Range(min=1, max=2000))
        ),
        vol.Optional("ledger_enabled", default=False): bool,
    },
    extra=vol.PREVENT_EXTRA,
)


def preferences_for_entry(hass, entry):
    """Adopt existing ledger settings with new display preferences."""
    saved = entry.options.get(OPTIONS_KEY)
    if saved is not None:
        return PREFERENCES_SCHEMA(saved)
    config = (
        hass.data.get("nio_telematics_car_dashboard", {})
        .get("settings", {})
        .get(entry.entry_id)
    )
    if not config:
        return PREFERENCES_SCHEMA({})
    return PREFERENCES_SCHEMA(
        {
            "ledger_enabled": True,
            "battery_capacity_kwh": config.get("capacity_kwh"),
            "full_range_km": config.get("full_range_km"),
            "evcc_connected": config.get("home_connected", ""),
            "evcc_history": config.get("home_history", ""),
        }
    )


def _vehicle(hass, entry, preferences):
    """Return dashboard metadata without exposing the VIN or credentials."""
    registry = er.async_get(hass)
    prefix = f"{entry.data['vin']}_"
    entities = {
        item.unique_id[len(prefix) :]: item.entity_id
        for item in er.async_entries_for_config_entry(registry, entry.entry_id)
        if item.unique_id.startswith(prefix)
        and item.unique_id[len(prefix) :] in SENSOR_KEYS
    }
    return {
        "entry_id": entry.entry_id,
        "name": entry.title,
        "entities": entities,
        "preferences": preferences_for_entry(hass, entry)
        if OPTIONS_KEY not in entry.options
        else PREFERENCES_SCHEMA(preferences),
        "ledger_available": entry.entry_id
        in hass.data.get("nio_telematics_car_dashboard", {}).get("recorders", {}),
    }


@websocket_api.websocket_command(
    {vol.Required("type"): "nio_telematics/vehicle_dashboard/get"}
)
@websocket_api.async_response
async def websocket_get(hass, connection, msg):
    connection.send_result(
        msg["id"],
        {
            "vehicles": [
                _vehicle(hass, entry, preferences_for_entry(hass, entry))
                for entry in hass.config_entries.async_entries(DOMAIN)
            ]
        },
    )


@websocket_api.websocket_command(
    {
        vol.Required("type"): "nio_telematics/vehicle_dashboard/save",
        vol.Required("entry_id"): str,
        vol.Required("preferences"): PREFERENCES_SCHEMA,
    }
)
@websocket_api.require_admin
@websocket_api.async_response
async def websocket_save(hass, connection, msg):
    entry = hass.config_entries.async_get_entry(msg["entry_id"])
    if entry is None or entry.domain != DOMAIN:
        connection.send_error(msg["id"], "invalid_entry", "Select a NIO vehicle")
        return
    for key in (
        "evcc_connected",
        "evcc_power",
        "evcc_history",
        "electricity_price",
        "reimbursement_rate",
    ):
        entity_id = msg["preferences"].get(key)
        if entity_id and not hass.states.get(entity_id):
            connection.send_error(msg["id"], "invalid_entity", f"{key} does not exist")
            return
    preferences = msg["preferences"]
    if preferences["ledger_enabled"]:
        if not preferences["battery_capacity_kwh"] or not preferences["full_range_km"]:
            connection.send_error(
                msg["id"],
                "missing_calibration",
                "History needs battery capacity and full-range calibration",
            )
            return
        entities = _vehicle(hass, entry, preferences)["entities"]
        if any(
            not hass.states.get(entities.get(key, ""))
            for key in ("odometer", "remaining_range")
        ):
            connection.send_error(
                msg["id"], "missing_source", "Enable NIO odometer and range first"
            )
            return
    hass.config_entries.async_update_entry(
        entry,
        options={**entry.options, OPTIONS_KEY: preferences},
    )
    try:
        await async_reconcile_ledger(hass, entry)
    except ValueError as err:
        connection.send_error(msg["id"], "history_error", str(err))
        return
    connection.send_result(msg["id"], _vehicle(hass, entry, preferences))


async def async_reconcile_ledger(hass, entry):
    """Start or pause optional history using the selected vehicle's own sensors."""
    preferences = preferences_for_entry(hass, entry)
    if OPTIONS_KEY not in entry.options:
        return  # Preserve existing dev.16 ledger installations.
    if "nio_telematics_car_dashboard" not in hass.data:
        return  # Frontend/HTTP is optional on headless installations.
    data = ledger_manager(hass)
    if not preferences["ledger_enabled"]:
        async with data["lock"]:
            recorder = data["recorders"].pop(entry.entry_id, None)
            if recorder:
                await recorder.async_stop()
                recorder.ledger.begin_new_epoch(recorder.settings)
                await recorder.store.async_save(deepcopy(recorder.ledger.data))
        return
    if not preferences["battery_capacity_kwh"] or not preferences["full_range_km"]:
        raise ValueError("History needs battery capacity and full-range calibration")
    entities = _vehicle(hass, entry, preferences)["entities"]
    if not all(key in entities for key in ("odometer", "remaining_range")):
        raise ValueError("Enable the NIO odometer and range entities for history")
    await async_configure_recorder(
        hass,
        entry.entry_id,
        {
            "odometer": entities["odometer"],
            "range": entities["remaining_range"],
            "soc": entities.get("battery_state_of_charge", ""),
            "home_connected": preferences["evcc_connected"],
            "home_history": preferences["evcc_history"],
            "capacity_kwh": preferences["battery_capacity_kwh"],
            "full_range_km": preferences["full_range_km"],
        },
    )


async def async_setup_vehicle_dashboard(hass):
    """Register the opt-in card without creating a view."""
    websocket_api.async_register_command(hass, websocket_get)
    websocket_api.async_register_command(hass, websocket_save)
    path = Path(__file__).with_name("nio-vehicle-card.js")
    digest = await hass.async_add_executor_job(
        lambda: sha256(path.read_bytes()).hexdigest()[:12]
    )
    url = "/nio_telematics/nio-vehicle-card.js"
    await hass.http.async_register_static_paths(
        [StaticPathConfig(url, str(path), False)]
    )
    frontend.add_extra_js_url(hass, f"{url}?v={digest}")
