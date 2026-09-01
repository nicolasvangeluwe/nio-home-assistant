"""Sensors for NIO Open Telematics."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE, UnitOfElectricCurrent, UnitOfLength
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .coordinator import NioDataUpdateCoordinator
from .entity import NioEntity
from .models import NioVehicleData


@dataclass(frozen=True, kw_only=True)
class NioSensorDescription(SensorEntityDescription):
    """Describe a NIO sensor."""

    value_fn: Callable[[NioVehicleData], str | float | datetime | None]


SENSORS: tuple[NioSensorDescription, ...] = (
    NioSensorDescription(
        key="battery_state_of_charge",
        translation_key="battery_state_of_charge",
        device_class=SensorDeviceClass.BATTERY,
        native_unit_of_measurement=PERCENTAGE,
        value_fn=lambda data: data.soc_status.soc,
    ),
    NioSensorDescription(
        key="remaining_range",
        translation_key="remaining_range",
        device_class=SensorDeviceClass.DISTANCE,
        native_unit_of_measurement=UnitOfLength.KILOMETERS,
        value_fn=lambda data: data.soc_status.remaining_range,
    ),
    NioSensorDescription(
        key="charging_state",
        translation_key="charging_state",
        value_fn=lambda data: data.soc_status.charging_state,
    ),
    NioSensorDescription(
        key="charging_target",
        translation_key="charging_target",
        native_unit_of_measurement=PERCENTAGE,
        value_fn=lambda data: data.soc_status.charging_target,
    ),
    NioSensorDescription(
        key="maximum_soc",
        translation_key="maximum_soc",
        native_unit_of_measurement=PERCENTAGE,
        entity_registry_enabled_default=False,
        value_fn=lambda data: data.soc_status.maximum_soc,
    ),
    NioSensorDescription(
        key="high_voltage_battery_current",
        translation_key="high_voltage_battery_current",
        device_class=SensorDeviceClass.CURRENT,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        entity_registry_enabled_default=False,
        value_fn=lambda data: data.soc_status.high_voltage_battery_current,
    ),
    NioSensorDescription(
        key="data_timestamp",
        translation_key="data_timestamp",
        device_class=SensorDeviceClass.TIMESTAMP,
        value_fn=lambda data: data.soc_status.event_time,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    coordinator: NioDataUpdateCoordinator = entry.runtime_data
    async_add_entities(NioSensor(coordinator, description) for description in SENSORS)


class NioSensor(NioEntity, SensorEntity):
    """Representation of a NIO telemetry sensor."""

    entity_description: NioSensorDescription

    def __init__(
        self,
        coordinator: NioDataUpdateCoordinator,
        description: NioSensorDescription,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        vin = coordinator.config_entry.data["vin"]
        self._attr_unique_id = f"{vin}_{description.key}"

    @property
    def native_value(self) -> str | float | datetime | None:
        return self.entity_description.value_fn(self.coordinator.data)
