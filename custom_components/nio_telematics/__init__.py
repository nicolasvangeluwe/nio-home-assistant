"""NIO Open Telematics integration."""

from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers import config_entry_oauth2_flow
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers import issue_registry as ir
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import NioApiClient
from .car_dashboard import async_setup_dashboard
from .companion_coordinator import CompanionDataUpdateCoordinator
from .companion_transport import CompanionVehicleClient, is_persistent_credential
from .const import (
    API_BASE_URL,
    COMPANION_API_ORIGIN,
    CONF_COMPANION_CREDENTIAL,
    CONF_CONNECTION_METHOD,
    CONF_SCOPE_REVISION,
    CONNECTION_COMPANION,
    DOMAIN,
    OAUTH_SCOPE_REVISION,
    PLATFORMS,
)
from .coordinator import NioDataUpdateCoordinator
from .pacing import NioRequestPacer
from .vehicle_dashboard import async_reconcile_ledger, async_setup_vehicle_dashboard

type NioConfigEntry = ConfigEntry[
    NioDataUpdateCoordinator | CompanionDataUpdateCoordinator
]
CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)
_LOGGER = logging.getLogger(__name__)


async def _async_dashboard_options_updated(
    hass: HomeAssistant, entry: NioConfigEntry
) -> None:
    """Apply optional dashboard changes without resetting NIO OAuth telemetry."""
    if entry.entry_id in hass.data.get("nio_telematics_dashboard_restoring", set()):
        return  # Restore applies the validated settings after replacing the archive.
    try:
        await async_reconcile_ledger(hass, entry)
        hass.data.setdefault("nio_telematics_dashboard_errors", {}).pop(
            entry.entry_id, None
        )
    except ValueError as err:
        hass.data.setdefault("nio_telematics_dashboard_errors", {})[entry.entry_id] = (
            str(err)
        )
        _LOGGER.warning("NIO dashboard history configuration: %s", err)


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Load the optional local ledger without requiring NIO API availability."""
    # NIO telemetry is usable on installations without the optional frontend.
    if getattr(hass, "http", None) is not None:
        await async_setup_dashboard(hass)
        await async_setup_vehicle_dashboard(hass)
    return True


async def async_setup_entry(hass: HomeAssistant, entry: NioConfigEntry) -> bool:
    """Set up NIO Open Telematics from a config entry."""
    if entry.data.get(CONF_CONNECTION_METHOD) == CONNECTION_COMPANION:
        credential = entry.data.get(CONF_COMPANION_CREDENTIAL, "")
        if not is_persistent_credential(credential):
            raise ConfigEntryAuthFailed(
                "A persistent Companion HA credential is required"
            )
        client = CompanionVehicleClient(
            async_get_clientsession(hass),
            api_origin=COMPANION_API_ORIGIN,
            credential=credential,
        )
        coordinator = CompanionDataUpdateCoordinator(hass, entry, client)
    else:
        coordinator = await _async_direct_coordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()
    if entry.data.get(CONF_CONNECTION_METHOD) != CONNECTION_COMPANION:
        ir.async_delete_issue(hass, DOMAIN, f"companion_source_{entry.entry_id}")
    entry.runtime_data = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(_async_dashboard_options_updated))
    await _async_dashboard_options_updated(hass, entry)
    return True


async def _async_direct_coordinator(hass, entry):
    """Legacy entries default to Direct, with the same shared NIO request budget."""
    if entry.data.get(CONF_SCOPE_REVISION) != OAUTH_SCOPE_REVISION:
        raise ConfigEntryAuthFailed(
            "NIO telemetry permissions have changed; reauthentication is required"
        )
    implementation = (
        await config_entry_oauth2_flow.async_get_config_entry_implementation(
            hass, entry
        )
    )
    oauth_session = config_entry_oauth2_flow.OAuth2Session(hass, entry, implementation)
    # One OAuth application may have multiple vehicles/config entries. Never
    # give each entry its own independent API request budget.
    pacers = hass.data.setdefault("nio_telematics_request_pacers", {})
    pacer = pacers.setdefault(implementation.client_id, NioRequestPacer())
    client = NioApiClient(
        oauth_session,
        API_BASE_URL,
        pacer=pacer,
    )
    return NioDataUpdateCoordinator(hass, entry, client)


async def async_unload_entry(hass: HomeAssistant, entry: NioConfigEntry) -> bool:
    """Unload a NIO config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
