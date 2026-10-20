"""Config-flow tests for NIO Open Telematics."""

from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock, patch

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

from custom_components.nio_telematics.config_flow import NioConfigFlow
from custom_components.nio_telematics.const import (
    CONF_SCOPE_REVISION,
    CONF_VEHICLE_NAME,
    CONF_VIN,
    DOMAIN,
    OAUTH_SCOPE_REVISION,
)


async def test_missing_application_credentials(hass: HomeAssistant) -> None:
    """The flow explains that application credentials are required."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] is FlowResultType.MENU
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {"next_step_id": "direct"}
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


async def test_oauth_records_current_scope_revision(hass: HomeAssistant) -> None:
    """A completed OAuth grant records the requested permission generation."""
    handler = NioConfigFlow()
    handler.hass = hass
    handler.context = {"source": config_entries.SOURCE_USER}

    result = await handler.async_oauth_create_entry(
        {"auth_implementation": "local", "token": {}}
    )

    assert result["type"] is FlowResultType.FORM
    assert handler._oauth_data[CONF_SCOPE_REVISION] == OAUTH_SCOPE_REVISION


async def test_reauth_offers_replacement_oauth_implementation(
    hass: HomeAssistant,
) -> None:
    """Reauth permits choosing a replacement for the old OAuth client."""
    handler = NioConfigFlow()
    handler.hass = hass
    expected_result = {"type": FlowResultType.EXTERNAL_STEP, "step_id": "auth"}

    with (
        patch.object(handler, "_get_reauth_entry"),
        patch.object(
            handler,
            "async_step_pick_implementation",
            AsyncMock(return_value=expected_result),
        ) as pick_implementation,
    ):
        result = await handler.async_step_reauth(
            {"auth_implementation": "nio-local"}
        )

    pick_implementation.assert_awaited_once_with()
    assert result == expected_result


async def test_reconfigure_offers_connection_source(hass: HomeAssistant) -> None:
    """Source selection does not mutate the entry or start a second collector."""
    handler = NioConfigFlow()
    handler.hass = hass
    expected_result = {"type": FlowResultType.FORM, "step_id": "pick_implementation"}
    with (
        patch.object(handler, "_get_reconfigure_entry"),
        patch.object(
            handler,
            "async_step_pick_implementation",
            AsyncMock(return_value=expected_result),
        ) as pick_implementation,
    ):
        result = await handler.async_step_reconfigure()
    pick_implementation.assert_not_awaited()
    assert result["type"] is FlowResultType.MENU
    assert result["menu_options"] == ["direct", "companion"]


async def test_reconfigure_success_preserves_vehicle_data(hass: HomeAssistant) -> None:
    """Only the OAuth fields change after the replacement grant succeeds."""
    handler = NioConfigFlow()
    handler.hass = hass
    handler.context = {"source": config_entries.SOURCE_RECONFIGURE}
    old_data = {
        "auth_implementation": "old-client",
        "token": {"access_token": "old-fixture"},
        CONF_VIN: "LJNABC12345678901",
        CONF_VEHICLE_NAME: "ET5 Touring",
        "other_setting": "retain",
    }
    entry = SimpleNamespace(data=old_data, options={"vehicle_dashboard": {"model": "auto"}})
    update = Mock(return_value={"type": FlowResultType.ABORT, "reason": "reconfigure_successful"})
    with (
        patch.object(handler, "_get_reconfigure_entry", return_value=entry),
        patch.object(handler, "async_update_reload_and_abort", update),
    ):
        result = await handler.async_oauth_create_entry(
            {"auth_implementation": "new-client", "token": {"access_token": "new-fixture"}}
        )
    saved = update.call_args.kwargs["data"]
    assert saved[CONF_VIN] == old_data[CONF_VIN]
    assert saved[CONF_VEHICLE_NAME] == old_data[CONF_VEHICLE_NAME]
    assert saved["other_setting"] == "retain"
    assert saved["auth_implementation"] == "new-client"
    assert saved["token"]["access_token"] == "new-fixture"
    assert saved[CONF_SCOPE_REVISION] == OAUTH_SCOPE_REVISION
    assert entry.data == old_data
    assert entry.options == {"vehicle_dashboard": {"model": "auto"}}
    assert result["reason"] == "reconfigure_successful"


async def test_reauth_success_uses_replacement_credentials(hass: HomeAssistant) -> None:
    """Reauth changes OAuth data without recreating the vehicle entry."""
    handler = NioConfigFlow()
    handler.hass = hass
    handler.context = {"source": config_entries.SOURCE_REAUTH}
    entry = SimpleNamespace(
        data={
            "auth_implementation": "old-client",
            "token": {"access_token": "old-fixture"},
            CONF_VIN: "LJNABC12345678901",
            CONF_VEHICLE_NAME: "ET5 Touring",
        }
    )
    update = Mock(return_value={"type": FlowResultType.ABORT, "reason": "reauth_successful"})
    with (
        patch.object(handler, "_get_reauth_entry", return_value=entry),
        patch.object(handler, "async_update_reload_and_abort", update),
    ):
        await handler.async_oauth_create_entry(
            {"auth_implementation": "new-client", "token": {"access_token": "new-fixture"}}
        )
    saved = update.call_args.kwargs["data"]
    assert saved[CONF_VIN] == entry.data[CONF_VIN]
    assert saved[CONF_VEHICLE_NAME] == entry.data[CONF_VEHICLE_NAME]
    assert saved["auth_implementation"] == "new-client"
    assert saved["token"]["access_token"] == "new-fixture"
    assert saved[CONF_SCOPE_REVISION] == OAUTH_SCOPE_REVISION
