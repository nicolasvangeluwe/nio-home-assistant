"""Optional bundled dashboard; recorded history lives outside HACS-installed files."""

import asyncio
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
from types import SimpleNamespace

import voluptuous as vol
from homeassistant.components import frontend, websocket_api
from homeassistant.components.http import StaticPathConfig
from homeassistant.const import EVENT_HOMEASSISTANT_STOP
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.storage import Store

from .const import DOMAIN as LEDGER_DOMAIN
from .coordinator import CarLedgerCoordinator
from .ledger import Ledger

NIO_DOMAIN = "nio_telematics"
DATA_KEY = "nio_telematics_car_dashboard"
CONFIG_SCHEMA = vol.Schema(
    {
        vol.Required("odometer"): cv.entity_id,
        vol.Required("range"): cv.entity_id,
        vol.Optional("soc", default=""): vol.Any("", cv.entity_id),
        vol.Optional("home_connected", default=""): vol.Any("", cv.entity_id),
        vol.Optional("home_history", default=""): vol.Any("", cv.entity_id),
        vol.Required("capacity_kwh"): vol.All(
            vol.Coerce(float), vol.Range(min=1, max=300)
        ),
        vol.Required("full_range_km"): vol.All(
            vol.Coerce(float), vol.Range(min=1, max=2000)
        ),
    }
)


def manager(hass):
    return hass.data[DATA_KEY]


def resolve(hass, entry_id):
    recorders = manager(hass)["recorders"]
    if not entry_id and len(recorders) == 1:
        return next(iter(recorders.values()))
    if entry_id not in recorders:
        raise ValueError("NIO dashboard has not been configured for this car")
    return recorders[entry_id]


@websocket_api.websocket_command(
    {
        vol.Required("type"): "nio_telematics/car_dashboard/get",
        vol.Optional("entry_id"): str,
    }
)
@websocket_api.async_response
async def websocket_get(hass, connection, msg):
    try:
        connection.send_result(msg["id"], resolve(hass, msg.get("entry_id")).snapshot())
    except ValueError as err:
        connection.send_error(msg["id"], "not_configured", str(err))


@websocket_api.websocket_command(
    {
        vol.Required("type"): "nio_telematics/car_dashboard/update",
        vol.Optional("entry_id"): str,
        vol.Required("action"): vol.In(
            [
                "edit_charge",
                "add_charge",
                "dismiss_candidate",
                "counter",
                "preferences",
                "recover_history",
            ]
        ),
        vol.Optional("values", default={}): dict,
    }
)
@websocket_api.require_admin
@websocket_api.async_response
async def websocket_update(hass, connection, msg):
    try:
        result = await resolve(hass, msg.get("entry_id")).mutate(
            msg["action"], msg["values"]
        )
    except (ValueError, KeyError, TypeError, StopIteration) as err:
        connection.send_error(msg["id"], "invalid_input", str(err))
        return
    connection.send_result(msg["id"], result)


async def start_recorder(hass, entry_id, settings):
    recorder = CarLedgerCoordinator(
        hass, SimpleNamespace(entry_id=entry_id, data=settings)
    )
    await recorder.async_start()
    manager(hass)["recorders"][entry_id] = recorder
    return recorder


async def async_configure_recorder(hass, entry_id, settings):
    """Apply source changes without erasing archived history or bridging baselines."""
    entry = hass.config_entries.async_get_entry(entry_id)
    if not entry or entry.domain != NIO_DOMAIN:
        raise ValueError("Select an existing NIO integration")
    settings = CONFIG_SCHEMA(settings)
    for key in ("odometer", "range", "soc", "home_connected", "home_history"):
        entity_id = settings[key]
        if entity_id and not hass.states.get(entity_id):
            raise ValueError(f"{key} entity does not exist")
    data = manager(hass)
    async with data["lock"]:
        old = data["recorders"].get(entry_id)
        if old and all(old.settings[key] == value for key, value in settings.items()):
            return old
        history_store = Store(
            hass, 1, f"{LEDGER_DOMAIN}.{entry_id}", atomic_writes=True
        )
        previous = (
            deepcopy(old.ledger.data) if old else await history_store.async_load()
        )
        previous_settings = data["settings"].get(entry_id) or (
            old.settings if old else None
        )
        energy_changed = previous_settings is not None and any(
            previous_settings.get(key) != settings[key]
            for key in ("odometer", "range", "soc", "capacity_kwh", "full_range_km")
        )
        if old:
            await old.async_stop()
        if energy_changed and previous:
            archived = Ledger(previous_settings, previous)
            archived.begin_new_epoch(settings)
            await history_store.async_save(deepcopy(archived.data))
        try:
            recorder = await start_recorder(hass, entry_id, settings)
            data["settings"][entry_id] = settings
            await data["store"].async_save(data["settings"])
        except Exception:
            if previous is not None:
                await history_store.async_save(previous)
            if old:
                await start_recorder(hass, entry_id, previous_settings)
            raise
        return recorder


@websocket_api.websocket_command(
    {
        vol.Required("type"): "nio_telematics/car_dashboard/configure",
        vol.Required("entry_id"): str,
        vol.Required("settings"): CONFIG_SCHEMA,
    }
)
@websocket_api.require_admin
@websocket_api.async_response
async def websocket_configure(hass, connection, msg):
    try:
        recorder = await async_configure_recorder(
            hass, msg["entry_id"], msg["settings"]
        )
    except (ValueError, vol.Invalid) as err:
        connection.send_error(msg["id"], "invalid_input", str(err))
        return
    connection.send_result(msg["id"], recorder.snapshot())


async def async_setup_dashboard(hass):
    if DATA_KEY in hass.data:
        return
    store = Store(hass, 1, "nio_telematics.car_dashboard_settings", atomic_writes=True)
    settings = await store.async_load() or {}
    hass.data[DATA_KEY] = {
        "store": store,
        "settings": settings,
        "recorders": {},
        "lock": asyncio.Lock(),
    }
    for handler in (websocket_get, websocket_update, websocket_configure):
        websocket_api.async_register_command(hass, handler)
    path = Path(__file__).with_name("car-ledger-card.js")
    digest = await hass.async_add_executor_job(
        lambda: sha256(path.read_bytes()).hexdigest()[:12]
    )
    url = "/nio_telematics/car-dashboard.js"
    await hass.http.async_register_static_paths(
        [StaticPathConfig(url, str(path), False)]
    )
    frontend.add_extra_js_url(hass, f"{url}?v={digest}")
    for entry_id, config in settings.items():
        entry = hass.config_entries.async_get_entry(entry_id)
        dashboard = entry.options.get("vehicle_dashboard", {}) if entry else {}
        if (
            entry
            and entry.domain == NIO_DOMAIN
            and dashboard.get("ledger_enabled", True)
        ):
            await start_recorder(hass, entry_id, CONFIG_SCHEMA(config))

    async def stop(event):
        for recorder in manager(hass)["recorders"].values():
            await recorder.async_stop()

    hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STOP, stop)
