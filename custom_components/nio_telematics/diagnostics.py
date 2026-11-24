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
    "companion_credential",
    "companion_vehicle_key",
}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry
) -> dict[str, Any]:
    """Return a strictly redacted diagnostic snapshot."""
    coordinator = entry.runtime_data
    polling = getattr(coordinator, "polling_controller", None)
    return {
        "entry": async_redact_data(dict(entry.data), TO_REDACT),
        "last_update_success": coordinator.last_update_success,
        "polling": polling.diagnostic_status() if polling is not None else None,
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
                "charging_state_observation": _charging_state_observation(
                    coordinator.data
                ),
                "endpoint_status": coordinator.data.endpoint_status,
                "connection_method": coordinator.data.connection_method,
                "source_generation": coordinator.data.source_generation,
            },
            TO_REDACT,
        ),
    }


def _charging_state_observation(data) -> dict[str, str | bool]:
    """Summarize the retained raw-field shape without disclosing its value."""
    if data.connection_method == "companion":
        payload_state = "raw_nio_payload_unavailable"
    else:
        payload = data.telemetry.get("soc_status")
        if not isinstance(payload, dict):
            payload_state = "no_payload_available"
        elif "chrg_state" not in payload or payload["chrg_state"] is None:
            payload_state = "not_in_retained_view"
        else:
            value = payload["chrg_state"]
            if isinstance(value, str) and not value:
                payload_state = "empty"
            elif isinstance(value, (str, int, float)) and not isinstance(value, bool):
                payload_state = "accepted_by_parser"
            else:
                payload_state = "rejected_type"
    return {
        "source": data.connection_method,
        "payload_view": "retained_sparse_merge",
        "payload_state": payload_state,
        "merged_value_available": data.soc_status.charging_state is not None,
    }
