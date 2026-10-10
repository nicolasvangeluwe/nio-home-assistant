"""NIO Open Telematics integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers import config_entry_oauth2_flow
from homeassistant.helpers import config_validation as cv

from .api import NioApiClient
from .car_dashboard import async_setup_dashboard
from .const import (
    API_BASE_URL,
    CONF_SCOPE_REVISION,
    DOMAIN,
    OAUTH_SCOPE_REVISION,
    PLATFORMS,
)
from .coordinator import NioDataUpdateCoordinator
from .pacing import NioRequestPacer

type NioConfigEntry = ConfigEntry[NioDataUpdateCoordinator]
CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Load the optional local ledger without requiring NIO API availability."""
    # NIO telemetry is usable on installations without the optional frontend.
    if getattr(hass, "http", None) is not None:
        await async_setup_dashboard(hass)
    return True


async def async_setup_entry(hass: HomeAssistant, entry: NioConfigEntry) -> bool:
    """Set up NIO Open Telematics from a config entry."""
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
    coordinator = NioDataUpdateCoordinator(hass, entry, client)
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: NioConfigEntry) -> bool:
    """Unload a NIO config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
