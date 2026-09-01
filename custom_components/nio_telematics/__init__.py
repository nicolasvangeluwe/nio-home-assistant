"""NIO Open Telematics integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_entry_oauth2_flow

from .api import NioApiClient
from .const import API_BASE_URL, PLATFORMS
from .coordinator import NioDataUpdateCoordinator

type NioConfigEntry = ConfigEntry[NioDataUpdateCoordinator]


async def async_setup_entry(hass: HomeAssistant, entry: NioConfigEntry) -> bool:
    """Set up NIO Open Telematics from a config entry."""
    implementation = await config_entry_oauth2_flow.async_get_config_entry_implementation(
        hass, entry
    )
    oauth_session = config_entry_oauth2_flow.OAuth2Session(
        hass, entry, implementation
    )
    client = NioApiClient(
        oauth_session,
        API_BASE_URL,
    )
    coordinator = NioDataUpdateCoordinator(hass, entry, client)
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: NioConfigEntry) -> bool:
    """Unload a NIO config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
