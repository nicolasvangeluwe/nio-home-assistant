"""Config-flow tests for NIO Open Telematics."""

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

from custom_components.nio_telematics.const import (
    CONF_VEHICLE_NAME,
    CONF_VIN,
    DOMAIN,
)
from custom_components.nio_telematics.config_flow import NioConfigFlow


async def test_missing_application_credentials(hass: HomeAssistant) -> None:
    """The flow explains that application credentials are required."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "missing_credentials"


async def test_vehicle_step_rejects_invalid_vin(hass: HomeAssistant) -> None:
    """A malformed VIN never creates a config entry."""
    # Exercise our post-OAuth form directly; redirect mechanics belong to HA core.
    handler = NioConfigFlow()
    handler.hass = hass
    handler._oauth_data = {"auth_implementation": "local", "token": {}}
    result = await handler.async_step_vehicle(
        {CONF_VEHICLE_NAME: "NIO", CONF_VIN: "invalid"}
    )
    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {CONF_VIN: "invalid_vin"}
