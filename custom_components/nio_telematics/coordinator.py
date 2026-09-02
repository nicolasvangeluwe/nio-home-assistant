"""Data coordinator for NIO Open Telematics."""

from __future__ import annotations

from datetime import UTC, datetime
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import (
    NioApiClient,
    NioApiError,
    NioAuthenticationError,
    NioPermissionError,
    NioResourceNotFoundError,
)
from .const import CONF_VIN, DEFAULT_SCAN_INTERVAL, DOMAIN
from .models import NioVehicleData


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
            update_interval=DEFAULT_SCAN_INTERVAL,
            config_entry=entry,
        )
        self._client = client
        self._vin = entry.data[CONF_VIN]

    async def _async_update_data(self) -> NioVehicleData:
        try:
            vehicle_status = await self._client.async_get_latest_vehicle_status(
                self._vin
            )
            try:
                energy_status = await self._client.async_get_soc_status(self._vin)
            except NioResourceNotFoundError:
                energy_status = None
        except (NioAuthenticationError, NioPermissionError) as err:
            raise ConfigEntryAuthFailed(str(err)) from err
        except NioApiError as err:
            raise UpdateFailed(str(err)) from err
        if energy_status is None:
            soc_status = vehicle_status
        else:
            soc_status = type(vehicle_status)(
                soc=vehicle_status.soc
                if vehicle_status.soc is not None
                else energy_status.soc,
                remaining_range=energy_status.remaining_range,
                charging_state=energy_status.charging_state
                if energy_status.charging_state is not None
                else vehicle_status.charging_state,
                charging_target=energy_status.charging_target,
                maximum_soc=energy_status.maximum_soc,
                high_voltage_battery_current=(
                    energy_status.high_voltage_battery_current
                ),
                event_time=max(
                    filter(
                        None,
                        [vehicle_status.event_time, energy_status.event_time],
                    ),
                    default=None,
                ),
            )
        return NioVehicleData(
            vin=self._vin,
            soc_status=soc_status,
            fetched_at=datetime.now(UTC),
        )
