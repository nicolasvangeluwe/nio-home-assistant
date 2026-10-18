"""Config flow for NIO Open Telematics."""

from __future__ import annotations

import logging
from collections.abc import Mapping
from typing import Any, override

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers import config_entry_oauth2_flow, selector

from .const import (
    CONF_SCOPE_REVISION,
    CONF_VEHICLE_NAME,
    CONF_VIN,
    DOMAIN,
    OAUTH_SCOPE_REVISION,
)
from .models import normalize_vin
from .vehicle_dashboard import (
    COST_PREFERENCES,
    LANGUAGES,
    MODELS,
    OPTIONS_KEY,
    PREFERENCES_SCHEMA,
    SOURCE_PREFERENCES,
    preferences_for_entry,
)


class NioConfigFlow(config_entry_oauth2_flow.AbstractOAuth2FlowHandler, domain=DOMAIN):
    """Configure a NIO vehicle through OAuth Authorization Code + PKCE."""

    VERSION = 1

    DOMAIN = DOMAIN

    @staticmethod
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> NioOptionsFlow:
        """Offer a reusable vehicle dashboard without changing OAuth settings."""
        return NioOptionsFlow()

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
        data = {**data, CONF_SCOPE_REVISION: OAUTH_SCOPE_REVISION}
        if self.source in (
            config_entries.SOURCE_REAUTH,
            config_entries.SOURCE_RECONFIGURE,
        ):
            reauth_entry = (
                self._get_reauth_entry()
                if self.source == config_entries.SOURCE_REAUTH
                else self._get_reconfigure_entry()
            )
            return self.async_update_reload_and_abort(
                reauth_entry,
                data={**reauth_entry.data, **data},
            )
        self._oauth_data = data
        return await self.async_step_vehicle()

    async def async_step_reauth(
        self, entry_data: Mapping[str, Any]
    ) -> config_entries.ConfigFlowResult:
        """Re-run OAuth flow when the existing token/scopes are no longer valid."""
        self._get_reauth_entry()
        # Do not force the old client: it may have been deleted or replaced.
        # A successful OAuth callback updates the existing vehicle entry.
        return await self.async_step_pick_implementation()

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Let the owner choose different application credentials."""
        self._get_reconfigure_entry()
        return await self.async_step_pick_implementation()

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


class NioOptionsFlow(config_entries.OptionsFlow):
    """Edit optional dashboard sources; the NIO telemetry remains independent."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            current = preferences_for_entry(self.hass, self.config_entry)
            preferences = PREFERENCES_SCHEMA({**current, **user_input})
            if preferences["ledger_enabled"] and not all(
                preferences[key] for key in ("battery_capacity_kwh", "full_range_km")
            ):
                errors["base"] = "ledger_calibration_required"
            elif any(preferences[key] for key in COST_PREFERENCES) and not all(
                preferences[key] for key in COST_PREFERENCES
            ):
                errors["base"] = "incomplete_cost_sources"
            else:
                return self.async_create_entry(
                    title="",
                    data={**self.config_entry.options, OPTIONS_KEY: preferences},
                )
        current = preferences_for_entry(self.hass, self.config_entry)
        entity = selector.EntitySelector(selector.EntitySelectorConfig())
        fields: dict[Any, Any] = {
            vol.Required("model", default=current["model"]): selector.SelectSelector(
                selector.SelectSelectorConfig(options=list(MODELS))
            ),
            vol.Required(
                "language", default=current["language"]
            ): selector.SelectSelector(
                selector.SelectSelectorConfig(options=list(LANGUAGES))
            ),
        }
        for key in (
            *SOURCE_PREFERENCES,
            *COST_PREFERENCES,
            "evcc_connected",
            "evcc_power",
            "evcc_history",
            "electricity_price",
            "reimbursement_rate",
        ):
            fields[vol.Optional(key, default=current[key])] = vol.Any("", entity)
        fields[
            vol.Optional(
                "battery_capacity_kwh",
                default=current["battery_capacity_kwh"],
            )
        ] = vol.Any(
            None,
            selector.NumberSelector(
                selector.NumberSelectorConfig(
                    min=1,
                    max=300,
                    step=0.1,
                    mode=selector.NumberSelectorMode.BOX,
                )
            ),
        )
        fields[vol.Optional("full_range_km", default=current["full_range_km"])] = (
            vol.Any(
                None,
                selector.NumberSelector(
                    selector.NumberSelectorConfig(
                        min=1, max=2000, step=1, mode=selector.NumberSelectorMode.BOX
                    )
                ),
            )
        )
        fields[vol.Optional("ledger_enabled", default=current["ledger_enabled"])] = (
            selector.BooleanSelector()
        )
        return self.async_show_form(
            step_id="init", data_schema=vol.Schema(fields), errors=errors
        )
