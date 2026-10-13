"""Optional, per-vehicle dashboard preferences and entity discovery."""

from __future__ import annotations

import asyncio
from copy import deepcopy
from pathlib import Path

import voluptuous as vol
from homeassistant.components import websocket_api
from homeassistant.components.http import StaticPathConfig
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.storage import Store
from homeassistant.util import dt as dt_util

from .car_dashboard import async_configure_recorder, start_recorder
from .car_dashboard import manager as ledger_manager
from .car_dashboard.cost_split import SOURCE_KEYS as COST_SOURCE_KEYS
from .car_dashboard.ledger import Ledger
from .const import DOMAIN
from .dashboard_backup import history_summary, make_backup, parse_backup

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
SOURCE_PREFERENCES = {
    "soc_entity": "battery_state_of_charge",
    "range_entity": "remaining_range",
    "odometer_entity": "odometer",
    "charging_state_entity": "charging_state",
    "charge_limit_entity": "maximum_soc",
}
COST_PREFERENCES = {f"cost_{key}": key for key in COST_SOURCE_KEYS}
ENTITY_PREFERENCES = (
    *SOURCE_PREFERENCES,
    *COST_PREFERENCES,
    "evcc_connected",
    "evcc_power",
    "evcc_history",
    "electricity_price",
    "reimbursement_rate",
)
PREFERENCES_SCHEMA = vol.Schema(
    {
        vol.Optional("model", default="auto"): vol.In(MODELS),
        vol.Optional("language", default="auto"): vol.In(LANGUAGES),
        vol.Optional("soc_entity", default=""): vol.Any("", cv.entity_id),
        vol.Optional("range_entity", default=""): vol.Any("", cv.entity_id),
        vol.Optional("odometer_entity", default=""): vol.Any("", cv.entity_id),
        vol.Optional("charging_state_entity", default=""): vol.Any("", cv.entity_id),
        vol.Optional("charge_limit_entity", default=""): vol.Any("", cv.entity_id),
        **{
            vol.Optional(key, default=""): vol.Any("", cv.entity_id)
            for key in COST_PREFERENCES
        },
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
    config = (
        hass.data.get("nio_telematics_car_dashboard", {})
        .get("settings", {})
        .get(entry.entry_id)
    )
    if saved is not None:
        legacy_costs = (config or {}).get("cost_sources", {})
        return PREFERENCES_SCHEMA(
            {
                **{
                    key: legacy_costs.get(source, "")
                    for key, source in COST_PREFERENCES.items()
                    if key not in saved
                },
                **saved,
            }
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
            **{
                key: config.get("cost_sources", {}).get(source, "")
                for key, source in COST_PREFERENCES.items()
            },
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
    configured = PREFERENCES_SCHEMA(preferences)
    native_entities = dict(entities)
    entities.update(
        {
            sensor_key: configured[preference_key]
            for preference_key, sensor_key in SOURCE_PREFERENCES.items()
            if configured[preference_key]
        }
    )
    return {
        "entry_id": entry.entry_id,
        "name": entry.title,
        "entities": entities,
        "native_entities": native_entities,
        "preferences": configured,
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
    for key in ENTITY_PREFERENCES:
        entity_id = msg["preferences"].get(key)
        if entity_id and not hass.states.get(entity_id):
            connection.send_error(msg["id"], "invalid_entity", f"{key} does not exist")
            return
    preferences = msg["preferences"]
    selected_costs = [preferences[key] for key in COST_PREFERENCES]
    if any(selected_costs) and not all(selected_costs):
        connection.send_error(
            msg["id"],
            "incomplete_cost_sources",
            "Set all five recorded-cost sources or leave them empty",
        )
        return
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
                msg["id"],
                "missing_source",
                "Select available odometer and range entities",
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


def _check_import_preferences(hass, entry, preferences):
    """Require an imported configuration to be usable on this HA."""
    configured = PREFERENCES_SCHEMA(preferences)
    for key in ENTITY_PREFERENCES:
        entity_id = configured[key]
        if entity_id and not hass.states.get(entity_id):
            raise ValueError(f"{key} entity does not exist on this Home Assistant")
    selected_costs = [configured[key] for key in COST_PREFERENCES]
    if any(selected_costs) and not all(selected_costs):
        raise ValueError("Set all five recorded-cost sources or leave them empty")
    if configured["ledger_enabled"]:
        if not configured["battery_capacity_kwh"] or not configured["full_range_km"]:
            raise ValueError(
                "History needs battery capacity and full-range calibration"
            )
        entities = _vehicle(hass, entry, configured)["entities"]
        if any(
            not hass.states.get(entities.get(key, ""))
            for key in ("odometer", "remaining_range")
        ):
            raise ValueError("Select available odometer and range entities for history")
    return configured


def _check_import_history(hass, preferences, history):
    """Exercise the current reader on a copy before replacing live history."""
    if history is None:
        return
    settings = {
        "capacity_kwh": preferences["battery_capacity_kwh"] or 90,
        "full_range_km": preferences["full_range_km"] or 557,
    }
    try:
        Ledger(settings, history).snapshot(
            dt_util.utcnow().timestamp(), hass.config.time_zone
        )
    except (ValueError, KeyError, TypeError, IndexError, ZeroDivisionError) as err:
        raise ValueError("Backup history cannot be read by this version") from err


async def _read_history(hass, entry_id):
    data = ledger_manager(hass)
    recorder = data["recorders"].get(entry_id)
    if recorder:
        async with recorder.lock:
            return deepcopy(recorder.ledger.data)
    return await Store(
        hass, 1, f"nio_car_dashboard.{entry_id}", atomic_writes=True
    ).async_load()


@websocket_api.websocket_command(
    {
        vol.Required("type"): "nio_telematics/vehicle_dashboard/backup",
        vol.Required("entry_id"): str,
        vol.Required("action"): vol.In(("export", "preview", "restore")),
        vol.Optional("backup"): dict,
        vol.Optional("expected_revision"): vol.Any(None, int),
        vol.Optional("confirmation"): str,
    }
)
@websocket_api.require_admin
@websocket_api.async_response
async def websocket_backup(hass, connection, msg):
    """Export or deliberately restore a single car's optional dashboard data."""
    entry = hass.config_entries.async_get_entry(msg["entry_id"])
    if entry is None or entry.domain != DOMAIN:
        connection.send_error(msg["id"], "invalid_entry", "Select a NIO vehicle")
        return
    try:
        if msg["action"] == "export":
            backup = make_backup(
                entry.data["vin"],
                preferences_for_entry(hass, entry),
                await _read_history(hass, entry.entry_id),
            )
            connection.send_result(msg["id"], backup)
            return
        preferences, history = parse_backup(msg.get("backup"), entry.data["vin"])
        preferences = _check_import_preferences(hass, entry, preferences)
        _check_import_history(hass, preferences, history)
        current = await _read_history(hass, entry.entry_id)
        current_summary = history_summary(current)
        if msg["action"] == "preview":
            connection.send_result(
                msg["id"],
                {
                    "imported": history_summary(history),
                    "current": current_summary,
                    "replaces_history": history is not None,
                    "exported_at": msg["backup"]["exported_at"],
                },
            )
            return
        if msg.get("confirmation") != "RESTORE":
            raise ValueError("Confirm the restore after reviewing its preview")
        if msg.get("expected_revision", object()) != current_summary["revision"]:
            raise ValueError("History changed since preview; review the restore again")
        data = ledger_manager(hass)
        restore_locks = data.setdefault("restore_locks", {})
        lock = restore_locks.setdefault(entry.entry_id, asyncio.Lock())
        async with lock:
            current = await _read_history(hass, entry.entry_id)
            if history_summary(current)["revision"] != msg["expected_revision"]:
                raise ValueError(
                    "History changed since preview; review the restore again"
                )
            old_options = deepcopy(entry.options)
            old_settings = deepcopy(data["settings"].get(entry.entry_id))
            recorder = data["recorders"].pop(entry.entry_id, None)
            if recorder:
                await recorder.async_stop()
            store = Store(
                hass, 1, f"nio_car_dashboard.{entry.entry_id}", atomic_writes=True
            )
            restoring = hass.data.setdefault(
                "nio_telematics_dashboard_restoring", set()
            )
            restoring.add(entry.entry_id)
            try:
                if history is not None:
                    await store.async_save(history)
                    # Imported evidence already belongs to its own source era.
                    # Do not compare it with this installation's old calibration.
                    data["settings"].pop(entry.entry_id, None)
                hass.config_entries.async_update_entry(
                    entry, options={**entry.options, OPTIONS_KEY: preferences}
                )
                await async_reconcile_ledger(hass, entry)
            except Exception:
                restarted = data["recorders"].pop(entry.entry_id, None)
                if restarted:
                    await restarted.async_stop()
                if current is not None:
                    await store.async_save(current)
                else:
                    await store.async_remove()
                hass.config_entries.async_update_entry(entry, options=old_options)
                if old_settings is not None:
                    data["settings"][entry.entry_id] = old_settings
                else:
                    data["settings"].pop(entry.entry_id, None)
                await data["store"].async_save(data["settings"])
                if recorder:
                    await start_recorder(hass, entry.entry_id, recorder.settings)
                raise
            finally:
                restoring.discard(entry.entry_id)
        connection.send_result(
            msg["id"],
            {
                "vehicle": _vehicle(hass, entry, preferences),
                "history": history_summary(await _read_history(hass, entry.entry_id)),
            },
        )
    except (ValueError, KeyError, TypeError, vol.Invalid) as err:
        connection.send_error(msg["id"], "invalid_backup", str(err))


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
        raise ValueError("Select available odometer and range entities for history")
    await async_configure_recorder(
        hass,
        entry.entry_id,
        {
            "odometer": entities["odometer"],
            "range": entities["remaining_range"],
            "soc": entities.get("battery_state_of_charge", ""),
            "home_connected": preferences["evcc_connected"],
            "home_history": preferences["evcc_history"],
            "cost_sources": (
                {source: preferences[key] for key, source in COST_PREFERENCES.items()}
                if all(preferences[key] for key in COST_PREFERENCES)
                else {}
            ),
            "capacity_kwh": preferences["battery_capacity_kwh"],
            "full_range_km": preferences["full_range_km"],
        },
    )


async def async_setup_vehicle_dashboard(hass):
    """Register the opt-in card without creating a view."""
    websocket_api.async_register_command(hass, websocket_get)
    websocket_api.async_register_command(hass, websocket_save)
    websocket_api.async_register_command(hass, websocket_backup)
    component_path = Path(__file__).parent
    await hass.http.async_register_static_paths(
        [
            StaticPathConfig(
                "/nio_telematics/nio-vehicle-card.js",
                str(component_path / "nio-vehicle-card.js"),
                False,
            ),
            StaticPathConfig(
                "/nio_telematics/et5-touring-hero.webp",
                str(component_path / "et5-touring-hero.webp"),
                False,
            ),
        ]
    )
