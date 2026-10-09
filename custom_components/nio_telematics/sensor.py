"""Sensors for NIO Open Telematics."""

from __future__ import annotations

import math
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from functools import partial
from typing import Any

from homeassistant.components.sensor import (
    RestoreSensor,
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    PERCENTAGE,
    EntityCategory,
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfEnergy,
    UnitOfLength,
    UnitOfSpeed,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant, State
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.recorder import DATA_INSTANCE
from sqlalchemy.exc import SQLAlchemyError

from .availability import availability_attributes, overall_availability
from .coordinator import NioDataUpdateCoordinator
from .entity import NioEntity
from .models import NioVehicleData


@dataclass(frozen=True, kw_only=True)
class NioSensorDescription(SensorEntityDescription):
    """Describe a NIO sensor."""

    value_fn: Callable[[NioVehicleData], Any]
    attributes_fn: Callable[[NioVehicleData], dict[str, Any]] | None = None
    source_endpoint: str | None = None


def _field(
    endpoint: str, field: str, scale: float = 1, offset: float = 0
) -> Callable[[NioVehicleData], Any]:
    def value(data: NioVehicleData) -> Any:
        current = data.telemetry.get(endpoint, {}).get(field)
        if current is None or isinstance(current, bool) or (scale == 1 and offset == 0):
            return current
        try:
            return float(current) * scale + offset
        except (TypeError, ValueError):
            return None

    return value


def _simple(
    key: str,
    name: str,
    endpoint: str,
    field: str,
    *,
    unit: str | None = None,
    device_class: SensorDeviceClass | None = None,
    scale: float = 1,
    offset: float = 0,
    enabled: bool = False,
) -> NioSensorDescription:
    return NioSensorDescription(
        key=key,
        name=name,
        native_unit_of_measurement=unit,
        device_class=device_class,
        entity_registry_enabled_default=enabled,
        value_fn=_field(endpoint, field, scale, offset),
        source_endpoint=endpoint,
    )


SENSORS: tuple[NioSensorDescription, ...] = (
    NioSensorDescription(
        key="api_availability",
        name="API availability",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: overall_availability(data.endpoint_status),
        attributes_fn=lambda data: availability_attributes(data.endpoint_status),
    ),
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
    _simple("vehicle_state", "Vehicle state", "vehicle_status", "vehl_state"),
    _simple("operation_mode", "Operation mode", "vehicle_status", "oprtn_mode"),
    _simple(
        "speed",
        "Speed",
        "vehicle_status",
        "speed",
        unit=UnitOfSpeed.KILOMETERS_PER_HOUR,
        scale=0.1,
    ),
    _simple(
        "odometer",
        "Odometer",
        "vehicle_status",
        "mileage",
        unit=UnitOfLength.KILOMETERS,
        device_class=SensorDeviceClass.DISTANCE,
        enabled=True,
    ),
    _simple(
        "vehicle_voltage",
        "Vehicle voltage",
        "vehicle_status",
        "vehl_totl_volt",
        unit=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        scale=0.1,
    ),
    _simple(
        "vehicle_current",
        "Vehicle current",
        "vehicle_status",
        "vehl_totl_curnt",
        unit=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        scale=0.1,
        offset=-1000,
    ),
    _simple("dc_dc_status", "DC-DC converter status", "vehicle_status", "dc_dc_sts"),
    _simple("gear", "Gear", "vehicle_status", "gear"),
    _simple(
        "insulation_resistance",
        "Insulation resistance",
        "vehicle_status",
        "insulatn_resis",
        unit="kΩ",
    ),
    _simple("comfort_mode", "Comfort mode", "vehicle_status", "comf_ena"),
    _simple(
        "vehicle_lock_status",
        "Vehicle lock status",
        "door_status",
        "vehicle_lock_status",
    ),
    _simple("fridge_mode", "Fridge mode", "fridge_status", "fridge_mod_sts"),
    _simple("fridge_power", "Fridge power", "fridge_status", "fridge_on_off_sts"),
    _simple("fridge_door", "Fridge door", "fridge_status", "fridge_door_sts"),
    _simple(
        "fridge_warning", "Fridge warning", "fridge_status", "fridge_door_open_warn_sts"
    ),
    _simple(
        "fridge_failure",
        "Fridge preconditioning failure",
        "fridge_status",
        "fridge_pre_cond_fail_sts",
    ),
    _simple(
        "fridge_target_temperature",
        "Fridge target temperature",
        "fridge_status",
        "fridge_set_temp",
        unit=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
    ),
    _simple("low_beam", "Low beam", "light_status", "lo_beam_on"),
    _simple("headlights", "Headlights", "light_status", "head_light_on"),
    _simple("high_beam", "High beam", "light_status", "hi_beam_on"),
    _simple("driving_mode", "Driving mode", "driving_data", "vcu_drvg_mod"),
    _simple(
        "steering_angle",
        "Steering angle",
        "driving_data",
        "steer_whl_rotn_ag",
        unit="°",
    ),
    _simple(
        "steering_speed",
        "Steering speed",
        "driving_data",
        "steer_whl_rotn_spd",
        unit="°/s",
    ),
    _simple(
        "accelerator_position",
        "Accelerator position",
        "driving_data",
        "aclrtn_pedal_posn",
        unit=PERCENTAGE,
    ),
    _simple(
        "average_speed",
        "Average speed",
        "driving_data",
        "average_speed",
        unit=UnitOfSpeed.KILOMETERS_PER_HOUR,
    ),
    _simple(
        "maximum_speed",
        "Maximum speed",
        "driving_data",
        "max_speed",
        unit=UnitOfSpeed.KILOMETERS_PER_HOUR,
    ),
    _simple(
        "minimum_speed",
        "Minimum speed",
        "driving_data",
        "min_speed",
        unit=UnitOfSpeed.KILOMETERS_PER_HOUR,
    ),
    _simple("heading", "Heading", "position_status", "heading", unit="°"),
    _simple("gps_mode", "GPS fix mode", "position_status", "mode"),
    _simple(
        "longitude_uncertainty",
        "Longitude uncertainty",
        "position_status",
        "longitude_uncertainty",
        unit=UnitOfLength.METERS,
    ),
    _simple(
        "latitude_uncertainty",
        "Latitude uncertainty",
        "position_status",
        "latitude_uncertainty",
        unit=UnitOfLength.METERS,
    ),
    _simple("trip_state", "Trip state", "trip_status", "trip_state"),
    _simple(
        "trip_distance",
        "Trip distance",
        "trip_status",
        "trip_odometer",
        unit=UnitOfLength.KILOMETERS,
        device_class=SensorDeviceClass.DISTANCE,
    ),
    _simple(
        "trip_energy",
        "Trip energy",
        "trip_status",
        "trip_eng",
        unit=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
    ),
    _simple(
        "trip_hv_accessory_energy",
        "Trip high-voltage accessory energy",
        "trip_status",
        "h_vass_eng_pct",
        unit=PERCENTAGE,
    ),
    _simple(
        "trip_lv_accessory_energy",
        "Trip low-voltage accessory energy",
        "trip_status",
        "lv_ass_eng_pct",
        unit=PERCENTAGE,
    ),
    _simple(
        "trip_driving_energy",
        "Trip driving energy",
        "trip_status",
        "dir_eng_pct",
        unit=PERCENTAGE,
    ),
    _simple(
        "trip_regenerated_energy",
        "Trip regenerated energy",
        "trip_status",
        "reg_eng_pct",
        unit=PERCENTAGE,
    ),
    _simple(
        "trip_heater_energy",
        "Trip heater energy",
        "trip_status",
        "hvh_eng_pct",
        unit=PERCENTAGE,
    ),
    _simple(
        "trip_adas_energy",
        "Trip ADAS energy",
        "trip_status",
        "adas_eng_pct",
        unit=PERCENTAGE,
    ),
    _simple(
        "trip_vehicle_odometer",
        "Trip vehicle odometer",
        "trip_status",
        "veh_odo_for_trip",
        unit=UnitOfLength.KILOMETERS,
        device_class=SensorDeviceClass.DISTANCE,
    ),
    _simple(
        "highest_cell_voltage",
        "Highest cell voltage",
        "extremum_data",
        "sin_btry_hist_volt",
        unit=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        scale=0.001,
    ),
    _simple(
        "lowest_cell_voltage",
        "Lowest cell voltage",
        "extremum_data",
        "sin_btry_lwst_volt",
        unit=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        scale=0.001,
    ),
    _simple(
        "highest_battery_temperature",
        "Highest battery temperature",
        "extremum_data",
        "highest_temp",
        unit=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        offset=-40,
    ),
    _simple(
        "lowest_battery_temperature",
        "Lowest battery temperature",
        "extremum_data",
        "lowest_temp",
        unit=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        offset=-40,
    ),
    _simple(
        "discharged_energy",
        "Discharged energy",
        "soc_status",
        "dump_enrgy",
        unit=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
    ),
    _simple(
        "soc_lock_limit", "SoC lock limit", "soc_status", "lock_soc", unit=PERCENTAGE
    ),
    _simple("soc_lock_status", "SoC lock status", "soc_status", "soc_lock_status"),
    _simple(
        "vehicle_to_load_status",
        "Vehicle-to-load status",
        "soc_status",
        "soc_v2lstatus",
    ),
    _simple(
        "battery_preheating", "Battery preheating", "heating_status", "hv_batt_pre_sts"
    ),
    _simple("battery_warm_up", "Battery warm-up", "heating_status", "btry_warm_up_sts"),
    _simple(
        "ambient_temperature",
        "Ambient temperature",
        "hvac_status",
        "amb_temp_c",
        unit=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
    ),
    _simple(
        "outside_temperature",
        "Outside temperature",
        "hvac_status",
        "outside_temp_c",
        unit=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
    ),
    _simple(
        "cabin_pm25",
        "Cabin PM2.5",
        "hvac_status",
        "pm2p5cabin",
        unit="µg/m³",
        device_class=SensorDeviceClass.PM25,
    ),
    _simple(
        "cabin_preconditioning", "Cabin preconditioning", "hvac_status", "cbn_pre_sts"
    ),
    _simple(
        "aftersales_odometer",
        "Aftersales odometer",
        "odometer_report",
        "value",
        unit=UnitOfLength.KILOMETERS,
        device_class=SensorDeviceClass.DISTANCE,
    ),
    _simple(
        "aftersales_odometer_time",
        "Aftersales odometer time",
        "odometer_report",
        "recorded_at",
    ),
    *tuple(
        NioSensorDescription(
            key=f"api_{endpoint}",
            name=f"API {endpoint.replace('_', ' ')}",
            entity_category=EntityCategory.DIAGNOSTIC,
            entity_registry_enabled_default=False,
            value_fn=lambda data, endpoint=endpoint: data.endpoint_status.get(endpoint),
            attributes_fn=lambda data, endpoint=endpoint: data.telemetry.get(
                endpoint, {}
            ),
        )
        for endpoint in (
            "vehicle_status",
            "door_status",
            "fridge_status",
            "light_status",
            "window_status",
            "driving_data",
            "position_status",
            "trip_status",
            "cell_status",
            "extremum_data",
            "soc_status",
            "heating_status",
            "hvac_status",
            "driving_motor",
            "alarm_signal",
            "odometer_report",
        )
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    coordinator: NioDataUpdateCoordinator = entry.runtime_data
    async_add_entities(
        NioRangeSensor(coordinator, description)
        if description.key == "remaining_range"
        else NioSocSensor(coordinator, description)
        if description.key == "battery_state_of_charge"
        else NioSensor(coordinator, description)
        for description in SENSORS
    )


class NioSensorEntity(NioEntity):
    """Shared NIO sensor implementation, independent of restoration policy."""

    entity_description: NioSensorDescription

    def __init__(
        self, coordinator: NioDataUpdateCoordinator, description: NioSensorDescription
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        vin = coordinator.config_entry.data["vin"]
        self._attr_unique_id = f"{vin}_{description.key}"

    @property
    def native_value(self) -> Any:
        return self.entity_description.value_fn(self.coordinator.data)

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        attributes = (
            self.entity_description.attributes_fn(self.coordinator.data)
            if self.entity_description.attributes_fn is not None
            else {}
        )
        if endpoint := self.entity_description.source_endpoint:
            attributes = {
                **attributes,
                "source_endpoint": endpoint,
                "endpoint_status": self.coordinator.data.endpoint_status.get(endpoint),
            }
        return attributes or None


class NioSensor(NioSensorEntity, SensorEntity):
    """Representation of a NIO telemetry sensor."""


class NioSocSensor(NioSensorEntity, RestoreSensor):
    """Keep the last SoC reported by NIO's sparse energy change feed."""

    _restored_soc: float | None = None
    _restored_sample_time: str | None = None

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        if (last_state := await self.async_get_last_state()) is not None:
            restored = _restorable_soc(last_state)
            if restored is not None:
                self._restored_soc, self._restored_sample_time = restored

    @property
    def native_value(self) -> float | None:
        value = self.coordinator.data.soc_status.soc
        if _soc_number(value) is not None:
            return value
        return self._restored_soc

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        sample = self.coordinator.data.soc_last_valid_at
        return {
            "source_endpoint": "soc_status",
            "last_valid_sample": sample.isoformat()
            if sample is not None
            else self._restored_sample_time,
            "data_retained": self.coordinator.data.soc_retained
            or (
                self.coordinator.data.soc_status.soc is None
                and self._restored_soc is not None
            ),
        }


class NioRangeSensor(NioSensorEntity, RestoreSensor):
    """Keep the last actual range when NIO omits it from sparse updates."""

    _restored_range: float | None = None
    _restored_sample_time: str | None = None

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        last_data = await self.async_get_last_sensor_data()
        if last_data is not None:
            value = _range_number(last_data.native_value)
            if value is not None:
                self._restored_range = value
                last_state = await self.async_get_last_state()
                if last_state is not None:
                    self._restored_sample_time = last_state.attributes.get(
                        "last_valid_sample"
                    )
                return
        # Migration from older releases: their final state can be 'unknown'
        # although Recorder still has a recent real reading. Query only this
        # entity, once, and only when Recorder is available.
        if DATA_INSTANCE not in self.hass.data or self.entity_id is None:
            return
        from homeassistant.components.recorder import get_instance, history

        try:
            states = await get_instance(self.hass).async_add_executor_job(
                partial(
                    history.get_significant_states,
                    self.hass,
                    datetime.now(UTC) - timedelta(days=7),
                    entity_ids=[self.entity_id],
                    include_start_time_state=False,
                    no_attributes=True,
                )
            )
        except (KeyError, RuntimeError, SQLAlchemyError):
            return
        if result := _last_recorded_range(states.get(self.entity_id, [])):
            self._restored_range, self._restored_sample_time = result

    @property
    def native_value(self) -> float | None:
        value = self.coordinator.data.soc_status.remaining_range
        if value is not None and math.isfinite(value) and value >= 0:
            return value
        return self._restored_range

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        sample: datetime | None = self.coordinator.data.remaining_range_last_valid_at
        return {
            "last_valid_sample": sample.isoformat()
            if sample is not None
            else self._restored_sample_time,
            "data_retained": self.coordinator.data.remaining_range_retained
            or (
                self.coordinator.data.soc_status.remaining_range is None
                and self._restored_range is not None
            ),
        }


def _range_number(value: Any) -> float | None:
    """Parse a finite nonnegative reading; reject unavailable/unknown states."""
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) and number >= 0 else None


def _soc_number(value: Any) -> float | None:
    """Accept only a finite SoC in the physical 0–100% range."""
    if isinstance(value, bool):
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) and 0 <= number <= 100 else None


def _restorable_soc(state: State) -> tuple[float, str | None] | None:
    """Never restore an old snapshot-derived zero after upgrading."""
    if state.attributes.get("source_endpoint") != "soc_status":
        return None
    if (value := _soc_number(state.state)) is None:
        return None
    return value, state.attributes.get("last_valid_sample")


def _last_recorded_range(states: list[State]) -> tuple[float, str] | None:
    """Skip newer unknowns and return the last actual Recorder sample."""
    for state in reversed(states):
        if (value := _range_number(state.state)) is not None:
            return value, state.last_changed.isoformat()
    return None
