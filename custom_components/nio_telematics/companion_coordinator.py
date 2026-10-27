"""Poll the authorized Companion cache without making upstream NIO requests."""

from __future__ import annotations

import logging
from dataclasses import replace
from datetime import UTC, datetime, timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers import issue_registry as ir
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .companion_transport import (
    CompanionFetchError,
    CompanionVehicleClient,
    field_is_current,
)
from .const import (
    COMPANION_CONNECTIONS_URL,
    CONF_COMPANION_VEHICLE_KEY,
    CONF_VIN,
    CONNECTION_COMPANION,
    DOMAIN,
)
from .models import NioSocStatus, NioVehicleData

# Existing sensor keys keep their identity. Fields absent from this contract
# remain unavailable instead of restoring a Direct-source reading as current.
SENSOR_FIELDS = {
    "battery_state_of_charge": "socPercent",
    "remaining_range": "rangeKm",
    "odometer": "odometerKm",
    "charging_target": "targetSocPercent",
    "maximum_soc": "maximumSocPercent",
    "high_voltage_battery_current": "batteryCurrentA",
    "vehicle_state": "vehicleState",
}
RETAINED_CORE_FIELDS = frozenset({"socPercent", "rangeKm", "odometerKm"})
TRANSIENT_RETENTION = timedelta(minutes=5)
_LOGGER = logging.getLogger(__name__)


def snapshot_to_vehicle(snapshot, previous=None) -> NioVehicleData:
    """Normalize verified physical units and preserve every source clock."""
    now = datetime.now(UTC)

    def quality(key, field):
        if field_is_current(field, now):
            return "valid"
        if (
            key in RETAINED_CORE_FIELDS
            and field.quality == "stale"
            and field.value is not None
            and field.source_timestamp is not None
            and field.received_at is not None
            and field.source_timestamp <= now
            and field.source_timestamp
            <= field.received_at
            <= now + timedelta(seconds=30)
        ):
            return "stale"
        return "unavailable"

    metadata = {
        key: {
            "quality": quality(key, field),
            "source_timestamp": field.source_timestamp,
            "received_at": field.received_at,
            "source_endpoint": field.source_endpoint,
        }
        for key, field in snapshot.fields.items()
    }

    def value(key):
        field = snapshot.fields[key]
        return field.value if metadata[key]["quality"] in {"valid", "stale"} else None

    def stamp(key):
        return snapshot.fields[key].source_timestamp

    def same(key, prior):
        return prior is not None and stamp(key) == prior

    charging_key = (
        "energyChargingState"
        if value("energyChargingState") is not None
        else "dynamicsChargingState"
    )
    metadata["charging_state"] = metadata[charging_key]
    times = [
        f.source_timestamp
        for key, f in snapshot.fields.items()
        if metadata[key]["quality"] == "valid"
    ]
    endpoints = {
        endpoint: "success"
        if any(
            metadata[key]["quality"] in {"valid", "stale"}
            for key, f in snapshot.fields.items()
            if f.source_endpoint == endpoint
        )
        else "stale_or_unavailable"
        for endpoint in ("soc_status", "vehicle_status")
    }
    return NioVehicleData(
        vin=snapshot.vin,
        soc_status=NioSocStatus(
            value("socPercent"),
            value("rangeKm"),
            value(charging_key),
            value("targetSocPercent"),
            value("maximumSocPercent"),
            value("batteryCurrentA"),
            max(times, default=None),
        ),
        fetched_at=now,
        telemetry={
            "soc_status": {},
            "vehicle_status": {
                "mileage": value("odometerKm"),
                "vehl_state": value("vehicleState"),
                "_odometer_sample_timestamp": stamp("odometerKm").timestamp()
                if stamp("odometerKm")
                else None,
                "_odometer_retained": metadata["odometerKm"]["quality"] == "stale"
                or same(
                    "odometerKm",
                    previous.field_metadata["odometerKm"]["source_timestamp"]
                    if previous and previous.field_metadata
                    else None,
                ),
            },
        },
        endpoint_status=endpoints,
        soc_last_valid_at=stamp("socPercent"),
        soc_retained=metadata["socPercent"]["quality"] == "stale"
        or same("socPercent", previous.soc_last_valid_at if previous else None),
        remaining_range_last_valid_at=stamp("rangeKm"),
        remaining_range_retained=metadata["rangeKm"]["quality"] == "stale"
        or same(
            "rangeKm", previous.remaining_range_last_valid_at if previous else None
        ),
        connection_method=CONNECTION_COMPANION,
        field_metadata=metadata,
        source_generation=snapshot.source_generation,
    )


def retain_transient_core(previous: NioVehicleData) -> NioVehicleData | None:
    """Display validated core readings without creating a new source sample."""
    metadata = previous.field_metadata or {}
    values = {
        "socPercent": previous.soc_status.soc,
        "rangeKm": previous.soc_status.remaining_range,
        "odometerKm": previous.telemetry.get("vehicle_status", {}).get("mileage"),
    }
    retained = {
        key: values[key]
        if metadata.get(key, {}).get("quality") == "valid"
        and metadata[key].get("source_timestamp") is not None
        and metadata[key].get("received_at") is not None
        else None
        for key in RETAINED_CORE_FIELDS
    }
    if all(value is None for value in retained.values()):
        return None
    stale_metadata = {
        key: {
            **field,
            "quality": "stale"
            if key in RETAINED_CORE_FIELDS and retained[key] is not None
            else "unavailable",
        }
        for key, field in metadata.items()
    }
    odometer = metadata.get("odometerKm", {})
    return replace(
        previous,
        soc_status=NioSocStatus(
            retained["socPercent"],
            retained["rangeKm"],
            None,
            None,
            None,
            None,
            previous.soc_status.event_time,
        ),
        telemetry={
            "soc_status": {},
            "vehicle_status": {
                "mileage": retained["odometerKm"],
                "vehl_state": None,
                "_odometer_sample_timestamp": odometer.get(
                    "source_timestamp"
                ).timestamp()
                if retained["odometerKm"] is not None
                else None,
                "_odometer_retained": retained["odometerKm"] is not None,
            },
        },
        endpoint_status={
            "soc_status": "temporary_unavailable",
            "vehicle_status": "temporary_unavailable",
        },
        field_metadata=stale_metadata,
        soc_retained=retained["socPercent"] is not None,
        remaining_range_retained=retained["rangeKm"] is not None,
    )


class CompanionDataUpdateCoordinator(DataUpdateCoordinator[NioVehicleData]):
    """A consumer credential survives upstream NIO reauthorization."""

    def __init__(
        self, hass: HomeAssistant, entry: ConfigEntry, client: CompanionVehicleClient
    ):
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=30),
            config_entry=entry,
        )
        self._client = client
        self._vin = entry.data[CONF_VIN]
        self._vehicle_key = entry.data[CONF_COMPANION_VEHICLE_KEY]
        self._issue_id = f"companion_source_{entry.entry_id}"
        self._last_good: NioVehicleData | None = None
        self._last_vehicle_key: str | None = None

    async def _async_update_data(self) -> NioVehicleData:
        try:
            snapshot = await self._client.async_fetch(
                expected_vin=self._vin, expected_vehicle_key=self._vehicle_key
            )
        except CompanionFetchError as err:
            self.update_interval = timedelta(seconds=max(30, err.retry_after or 30))
            _LOGGER.warning(
                "Companion cache read failed: kind=%s reason=%s status=%s "
                "retry_after=%s duration_ms=%s",
                err.kind,
                err.reason,
                err.status,
                err.retry_after,
                err.duration_ms,
            )
            if err.kind != "retry_later":
                self._last_good = None
                self._last_vehicle_key = None
            if err.kind == "consumer_reauthentication_required":
                ir.async_delete_issue(self.hass, DOMAIN, self._issue_id)
                raise ConfigEntryAuthFailed("Companion HA access was revoked") from None
            if err.kind in {"upstream_reauthorization_required", "source_disconnected"}:
                ir.async_create_issue(
                    self.hass,
                    DOMAIN,
                    self._issue_id,
                    is_fixable=False,
                    severity=ir.IssueSeverity.WARNING,
                    translation_key="companion_source_reconnect",
                    translation_placeholders={
                        "connections_url": COMPANION_CONNECTIONS_URL
                    },
                    learn_more_url=COMPANION_CONNECTIONS_URL,
                )
            if (
                err.kind == "retry_later"
                and self._last_good is not None
                and self._last_vehicle_key
                == self._vehicle_key
                == self.config_entry.data.get(CONF_COMPANION_VEHICLE_KEY)
                and self._last_good.vin == self._vin
                and self._last_good.connection_method == CONNECTION_COMPANION
                and self._last_good.source_generation is not None
                and self.data is not None
                and self.data.source_generation == self._last_good.source_generation
                and timedelta(0)
                <= datetime.now(UTC) - self._last_good.fetched_at
                <= TRANSIENT_RETENTION
                and (retained := retain_transient_core(self._last_good)) is not None
            ):
                return retained
            raise UpdateFailed(f"Companion: {err.kind}") from None
        ir.async_delete_issue(self.hass, DOMAIN, self._issue_id)
        self.update_interval = timedelta(seconds=30)
        vehicle = snapshot_to_vehicle(snapshot, self.data)
        self._last_good = vehicle
        self._last_vehicle_key = snapshot.vehicle_key
        return vehicle
