"""Config flow for NIO Open Telematics."""

from __future__ import annotations

import logging
from typing import Any, override

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.helpers import config_entry_oauth2_flow

from .const import CONF_VEHICLE_NAME, CONF_VIN, DOMAIN
from .models import normalize_vin


class NioConfigFlow(
    config_entry_oauth2_flow.AbstractOAuth2FlowHandler, domain=DOMAIN
):
    """Configure a NIO vehicle through OAuth Authorization Code + PKCE."""

    VERSION = 1

    DOMAIN = DOMAIN

    def __init__(self) -> None:
        super().__init__()
        self._oauth_data: dict[str, Any] = {}

    @property
    @override
    def logger(self) -> logging.Logger:
        """Return the flow logger."""
        return logging.getLogger(__name__)

    @override
    async def async_oauth_create_entry(
        self, data: dict[str, Any]
    ) -> config_entries.ConfigFlowResult:
        """Collect the vehicle identity after OAuth and create the entry."""
        self._oauth_data = data
        return await self.async_step_vehicle()

    async def async_step_vehicle(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Collect the VIN until the official vehicle-discovery schema is verified."""
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                vin = normalize_vin(user_input[CONF_VIN])
            except ValueError:
                errors[CONF_VIN] = "invalid_vin"
            else:
                await self.async_set_unique_id(vin)
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=user_input[CONF_VEHICLE_NAME].strip(),
                    data={
                        **self._oauth_data,
                        CONF_VIN: vin,
                        CONF_VEHICLE_NAME: user_input[CONF_VEHICLE_NAME].strip(),
                    },
                )
        return self.async_show_form(
            step_id="vehicle",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_VEHICLE_NAME): str,
                    vol.Required(CONF_VIN): str,
                }
            ),
            errors=errors,
        )
