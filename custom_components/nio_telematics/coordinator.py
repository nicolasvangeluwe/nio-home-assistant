"""Data coordinator for NIO Open Telematics."""

from __future__ import annotations

import logging
import math
import time
from dataclasses import replace
from datetime import UTC, datetime, timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import (
    ConfigEntryAuthFailed,
    OAuth2TokenRequestReauthError,
)
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import (
    NioApiClient,
    NioApiError,
    NioAuthenticationError,
    NioPermissionError,
    NioResourceNotFoundError,
)
from .const import CONF_VIN, DOMAIN
from .models import NioSocStatus, NioVehicleData, _event_datetime
from .polling import polling_settings_for_entry


class NioDataUpdateCoordinator(DataUpdateCoordinator[NioVehicleData]):
    """Fetch a coherent snapshot for one NIO vehicle."""

    _LOGGER = logging.getLogger(__name__)

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        client: NioApiClient,
    ) -> None:
        super().__init__(
            hass,
            logger=self._LOGGER,
            name=DOMAIN,
            update_interval=timedelta(
                seconds=polling_settings_for_entry(entry)["interval_seconds"]
            ),
            config_entry=entry,
        )
        self._client = client
        self._vin = entry.data[CONF_VIN]
        self._telemetry: dict[str, dict] = {}
        self._request_count = 0
        self._polling_refresh_count = 0
        self._polling_last_attempt_monotonic: float | None = None
        self._polling_auth_failed = False
        self._polling_transport_recovering = False
        self._background_index = 0
        self._joint_zero_pending: dict | None = None
        self._rejected_zero_at: dict[str, datetime] = {}

    _CHANGE_ENDPOINTS = (
        "door_status",
        "fridge_status",
        "light_status",
        "window_status",
        "driving_data",
        "position_status",
        "trip_status",
        "cell_status",
        "extremum_data",
        "heating_status",
        "hvac_status",
        "driving_motor",
        "alarm_signal",
    )
    _BACKGROUND_ENDPOINTS = (*_CHANGE_ENDPOINTS, "odometer_report")

    async def _async_update_data(self) -> NioVehicleData:
        """Fetch one resource per cycle: energy, energy, energy, background."""
        self._polling_refresh_count += 1
        self._polling_last_attempt_monotonic = time.monotonic()
        if (controller := getattr(self, "polling_controller", None)) is not None:
            controller.refresh_mode()
        previous = self.data
        endpoint_status = dict(previous.endpoint_status) if previous else {}
        energy_record = None
        vehicle_record = None
        energy_denied = endpoint_status.get("soc_status") == "permission_denied"
        resource = (
            "soc_status"
            if (not energy_denied and self._request_count % 4 != 3)
            or (energy_denied and self._request_count % 40 == 0)
            else (
                "vehicle_status"
                if self._background_index % 2 == 0
                else self._BACKGROUND_ENDPOINTS[
                    (self._background_index // 2) % len(self._BACKGROUND_ENDPOINTS)
                ]
            )
        )
        try:
            if resource == "vehicle_status":
                vehicle_record = await self._client.async_get_latest_vehicle_record(
                    self._vin
                )
                record = vehicle_record
            elif resource == "odometer_report":
                record = await self._client.async_get_odometer_report(self._vin)
            else:
                record = await self._client.async_get_change_record(self._vin, resource)
                if resource == "soc_status":
                    energy_record = record
            self._telemetry[resource] = (
                _merge_sparse_energy(self._telemetry.get(resource), record)
                if resource == "soc_status"
                else _retain_vehicle_odometer(self._telemetry.get(resource), record)
                if resource == "vehicle_status"
                else record
            )
            endpoint_status[resource] = "success"
        except NioResourceNotFoundError:
            endpoint_status[resource] = "no_recent_data"
        except NioPermissionError:
            endpoint_status[resource] = "permission_denied"
        except OAuth2TokenRequestReauthError as err:
            self._polling_auth_failed = True
            raise ConfigEntryAuthFailed(
                "NIO OAuth authorization expired; reauthentication is required"
            ) from err
        except NioAuthenticationError as err:
            self._polling_auth_failed = True
            raise ConfigEntryAuthFailed(str(err)) from err
        except NioApiError as err:
            # Keep optional-feed failures from pinning Direct to one endpoint.
            # Preserve the failed-update signal so HA still retries the update.
            self._polling_transport_recovering = True
            if (controller := getattr(self, "polling_controller", None)) is not None:
                controller.refresh_mode()
            self._request_count += 1
            if resource != "soc_status":
                self._background_index += 1
            raise UpdateFailed(str(err)) from err
        self._polling_auth_failed = False
        self._polling_transport_recovering = False
        if (controller := getattr(self, "polling_controller", None)) is not None:
            controller.refresh_mode()
        self._request_count += 1
        if resource != "soc_status":
            self._background_index += 1

        status = (
            previous.soc_status
            if previous
            else NioSocStatus(None, None, None, None, None, None, None)
        )
        soc_at = previous.soc_last_valid_at if previous else None
        range_at = previous.remaining_range_last_valid_at if previous else None
        soc_retained = _valid_soc(status.soc)
        range_retained = _valid_range(status.remaining_range)

        if vehicle_record is not None:
            snapshot = NioSocStatus.from_payload(vehicle_record)
            # The snapshot's SoC zero is a known placeholder. The energy feed
            # is authoritative; its separate field timestamps are retained.
            status = replace(
                status,
                charging_state=snapshot.charging_state or status.charging_state,
                event_time=max(
                    filter(None, (status.event_time, snapshot.event_time)),
                    default=None,
                ),
            )
            if (
                not _valid_range(status.remaining_range)
                and _valid_range(snapshot.remaining_range)
                and snapshot.remaining_range > 0
            ):
                status = replace(status, remaining_range=snapshot.remaining_range)
                range_at = snapshot.event_time
                range_retained = False

        if energy_record is not None:
            energy = NioSocStatus.from_payload(energy_record)
            field_times = energy_record.get("_field_timestamps", {})
            soc_event = _event_datetime(field_times.get("soc")) or energy.event_time
            range_event = (
                _event_datetime(field_times.get("remaining_range")) or energy.event_time
            )
            blocked_zero = self._confirm_joint_zero(
                energy, status, soc_event, range_event, soc_at, range_at
            )
            if (
                "soc" not in blocked_zero
                and _valid_soc(energy.soc)
                and _new_event(soc_event, soc_at, energy.soc, status.soc)
            ):
                status = replace(status, soc=energy.soc)
                soc_at = soc_event
                soc_retained = False
            if (
                "remaining_range" not in blocked_zero
                and _valid_range(energy.remaining_range)
                and _new_event(
                    range_event,
                    range_at,
                    energy.remaining_range,
                    status.remaining_range,
                )
            ):
                status = replace(status, remaining_range=energy.remaining_range)
                range_at = range_event
                range_retained = False
            status = replace(
                status,
                charging_state=energy.charging_state or status.charging_state,
                charging_target=energy.charging_target
                if energy.charging_target is not None
                else status.charging_target,
                maximum_soc=energy.maximum_soc
                if energy.maximum_soc is not None
                else status.maximum_soc,
                high_voltage_battery_current=energy.high_voltage_battery_current
                if energy.high_voltage_battery_current is not None
                else status.high_voltage_battery_current,
                event_time=max(
                    filter(None, (status.event_time, energy.event_time)),
                    default=None,
                ),
            )
        return NioVehicleData(
            vin=self._vin,
            soc_status=status,
            fetched_at=datetime.now(UTC),
            telemetry=dict(self._telemetry),
            endpoint_status=endpoint_status,
            soc_last_valid_at=soc_at,
            soc_retained=soc_retained,
            remaining_range_last_valid_at=range_at,
            remaining_range_retained=range_retained,
        )

    def _confirm_joint_zero(
        self, energy, previous, soc_at, range_at, previous_soc_at, previous_range_at
    ):
        """Confirm an abrupt joint zero only with later source evidence.

        Sixty seconds is a chosen confirmation window, not an API guarantee.
        Background polls/errors never call this method. Near-empty and initial
        zeroes remain valid. Both zero-field clocks must advance on a later
        successful read; cached pairs never mature. Accepted fields keep that
        confirming reading's actual NIO clocks, never the local read time.
        """
        clocks = {"soc": soc_at, "remaining_range": range_at}
        values = {"soc": energy.soc, "remaining_range": energy.remaining_range}
        pending = self._joint_zero_pending
        if pending and any(
            value is not None
            and value > 0
            and clocks[key] is not None
            and clocks[key] >= pending[key]
            for key, value in values.items()
        ):
            self._rejected_zero_at.update({key: pending[key] for key in clocks})
            self._joint_zero_pending = pending = None
        blocked = {
            key
            for key, value in values.items()
            if value == 0
            and clocks[key] is not None
            and key in self._rejected_zero_at
            and clocks[key] <= self._rejected_zero_at[key]
        }
        joint = (
            energy.soc == 0
            and energy.remaining_range == 0
            and soc_at is not None
            and range_at is not None
            and abs((soc_at - range_at).total_seconds()) <= 5
            and not blocked
        )
        if (
            pending is None
            and joint
            and previous.soc is not None
            and previous.soc > 1
            and previous.remaining_range is not None
            and previous.remaining_range > 0
            and _new_event(soc_at, previous_soc_at, 0, previous.soc)
            and _new_event(range_at, previous_range_at, 0, previous.remaining_range)
        ):
            pending = {"started": time.monotonic(), **clocks}
            self._joint_zero_pending = pending
        if pending:
            if joint:
                if time.monotonic() - pending["started"] >= 60 and all(
                    clocks[key] > pending[key] for key in clocks
                ):
                    self._joint_zero_pending = None
                    return blocked
            for key in clocks:
                if values[key] == 0 and clocks[key] is not None:
                    pending[key] = max(pending[key], clocks[key])
            blocked.update(key for key, value in values.items() if value == 0)
        return blocked


def _valid_range(value: float | None) -> bool:
    """Accept real zero from the energy feed, but no missing/nonfinite values."""
    return value is not None and math.isfinite(value) and value >= 0


def _valid_soc(value: float | None) -> bool:
    """Accept a real 0–100% reading only from the SoC change feed."""
    return value is not None and math.isfinite(value) and 0 <= value <= 100


def _new_event(
    timestamp: datetime | None,
    previous_timestamp: datetime | None,
    value: float,
    previous_value: float | None,
) -> bool:
    """Do not treat the overlapping window's same/older record as fresh."""
    if timestamp is not None and previous_timestamp is not None:
        return timestamp > previous_timestamp
    return previous_value != value


def _merge_sparse_energy(previous: dict | None, current: dict) -> dict:
    """Keep each field's latest event across overlapping sparse windows."""
    if not previous:
        return current
    merged = dict(previous)
    timestamps = dict(previous.get("_field_timestamps", {}))
    current_times = current.get("_field_timestamps", {})
    for key, value in current.items():
        if key in ("sample_timestamp", "_field_timestamps") or value is None:
            continue
        if (
            key in {"soc", "remaining_range"}
            and getattr(NioSocStatus.from_payload({key: value}), key) is None
        ):
            continue
        incoming = _event_datetime(current_times.get(key))
        stored = _event_datetime(timestamps.get(key))
        if stored is None or (incoming is not None and incoming >= stored):
            merged[key] = value
            timestamps[key] = current_times.get(key)
    merged["_field_timestamps"] = timestamps
    merged["sample_timestamp"] = max(
        previous.get("sample_timestamp") or 0,
        current.get("sample_timestamp") or 0,
    )
    return merged


def _valid_odometer(value: object) -> bool:
    """Reject missing, nonfinite and NIO's documented invalid mileage markers."""
    if value is None or isinstance(value, bool):
        return False
    try:
        number = float(value)
    except (TypeError, ValueError):
        return False
    return math.isfinite(number) and 0 <= number < 0xFFFFFFFE


def _retain_vehicle_odometer(previous: dict | None, current: dict) -> dict:
    """Keep only the last valid mileage when a latest snapshot omits it."""
    merged = dict(current)
    prior = previous or {}
    if _valid_odometer(current.get("mileage")):
        merged["_odometer_sample_timestamp"] = current.get("sample_timestamp")
        merged["_odometer_retained"] = False
    elif _valid_odometer(prior.get("mileage")):
        merged["mileage"] = prior["mileage"]
        merged["_odometer_sample_timestamp"] = prior.get(
            "_odometer_sample_timestamp", prior.get("sample_timestamp")
        )
        merged["_odometer_retained"] = True
    else:
        merged.pop("mileage", None)
    return merged
