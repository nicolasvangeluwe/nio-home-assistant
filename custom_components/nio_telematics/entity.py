"""Base entity for NIO Open Telematics."""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import NioDataUpdateCoordinator


class NioEntity(CoordinatorEntity[NioDataUpdateCoordinator]):
    """Base class shared by NIO entities."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: NioDataUpdateCoordinator) -> None:
        super().__init__(coordinator)
        vin = coordinator.config_entry.data["vin"]
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, vin)},
            manufacturer="NIO",
            name=coordinator.config_entry.title,
        )
