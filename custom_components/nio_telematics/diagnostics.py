"""Diagnostics for NIO Open Telematics."""

from __future__ import annotations

from typing import Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

TO_REDACT = {
    "access_token",
    "vin",
    "refresh_token",
    "client_id",
    "client_secret",
    "token",
}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry
) -> dict[str, Any]:
    """Return a strictly redacted diagnostic snapshot."""
    coordinator = entry.runtime_data
    return {
        "entry": async_redact_data(dict(entry.data), TO_REDACT),
        "last_update_success": coordinator.last_update_success,
        "data": async_redact_data(
            {
                "fetched_at": coordinator.data.fetched_at.isoformat(),
                "event_time": (
                    coordinator.data.soc_status.event_time.isoformat()
                    if coordinator.data.soc_status.event_time
                    else None
                ),
                "fields_available": {
                    field: value is not None
                    for field, value in {
                        "soc": coordinator.data.soc_status.soc,
                        "remaining_range": coordinator.data.soc_status.remaining_range,
                        "charging_state": coordinator.data.soc_status.charging_state,
                        "charging_target": coordinator.data.soc_status.charging_target,
                    }.items()
                },
            },
            TO_REDACT,
        ),
    }
