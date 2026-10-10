"""Coordinator authentication-failure regression tests."""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.config_entry_oauth2_flow import OAuth2TokenRequestReauthError
from homeassistant.helpers.update_coordinator import UpdateFailed

from custom_components.nio_telematics.api import NioApiError, NioResourceNotFoundError
from custom_components.nio_telematics.const import CONF_VIN
from custom_components.nio_telematics.coordinator import NioDataUpdateCoordinator


async def test_rejected_refresh_becomes_config_entry_auth_failure(
    hass: HomeAssistant,
) -> None:
    """Coordinator must surface a rejected grant to HA's reauth machinery."""
    entry = MagicMock()
    entry.data = {CONF_VIN: "LJNABC12345678901"}
    client = MagicMock()
    client.async_get_change_record = AsyncMock(
        side_effect=OAuth2TokenRequestReauthError(
            request_info=MagicMock(), domain="nio_telematics"
        )
    )
    coordinator = NioDataUpdateCoordinator(hass, entry, client)

    with pytest.raises(ConfigEntryAuthFailed, match="reauthentication is required"):
        await coordinator._async_update_data()


async def test_temporary_refresh_failure_remains_retryable(hass: HomeAssistant) -> None:
    """Temporary token-service errors must not become auth failures."""
    entry = MagicMock()
    entry.data = {CONF_VIN: "LJNABC12345678901"}
    client = MagicMock()
    client.async_get_change_record = AsyncMock(
        side_effect=NioApiError("NIO OAuth token service is temporarily unavailable")
    )
    coordinator = NioDataUpdateCoordinator(hass, entry, client)

    with pytest.raises(UpdateFailed, match="temporarily unavailable"):
        await coordinator._async_update_data()


async def test_range_survives_sparse_change_feed(hass: HomeAssistant) -> None:
    """A missing energy event and a vehicle placeholder must not erase range."""
    entry = MagicMock()
    entry.data = {CONF_VIN: "LJNABC12345678901"}
    client = MagicMock()
    client.async_get_latest_vehicle_record = AsyncMock(
        return_value={"soc": 0, "remaining_range": 0}
    )
    energy_records = iter([{"remaining_range": 213}, None])

    async def get_change_record(_vin: str, resource: str) -> dict:
        if resource == "soc_status":
            record = next(energy_records)
            if record is not None:
                return record
        raise NioResourceNotFoundError("No recent data")

    client.async_get_change_record = get_change_record
    client.async_get_odometer_report = AsyncMock(
        side_effect=NioResourceNotFoundError("No recent data")
    )
    coordinator = NioDataUpdateCoordinator(hass, entry, client)
    first = await coordinator._async_update_data()
    assert first.soc_status.remaining_range == 213
    assert not first.remaining_range_retained

    coordinator.async_set_updated_data(first)
    second = await coordinator._async_update_data()
    assert second.soc_status.remaining_range == 213
    assert second.remaining_range_retained


async def test_soc_prefers_change_feed_and_survives_empty_polls(
    hass: HomeAssistant,
) -> None:
    """A placeholder snapshot zero must never mask or replace actual SoC."""
    entry = MagicMock()
    entry.data = {CONF_VIN: "LJNABC12345678901"}
    client = MagicMock()
    client.async_get_latest_vehicle_record = AsyncMock(return_value={"soc": 0})
    energy_records = iter([{"soc": 38, "remaining_range": 213}, None])

    async def get_change_record(_vin: str, resource: str) -> dict:
        if resource == "soc_status":
            if (record := next(energy_records)) is not None:
                return record
        raise NioResourceNotFoundError("No recent data")

    client.async_get_change_record = get_change_record
    client.async_get_odometer_report = AsyncMock(
        side_effect=NioResourceNotFoundError("No recent data")
    )
    coordinator = NioDataUpdateCoordinator(hass, entry, client)
    first = await coordinator._async_update_data()
    assert first.soc_status.soc == 38
    assert not first.soc_retained

    coordinator.async_set_updated_data(first)
    second = await coordinator._async_update_data()
    assert second.soc_status.soc == 38
    assert second.soc_retained


async def test_snapshot_zero_is_not_presented_as_official_soc(
    hass: HomeAssistant,
) -> None:
    """Until an energy event arrives, the official SoC remains unknown."""
    entry = MagicMock()
    entry.data = {CONF_VIN: "LJNABC12345678901"}
    client = MagicMock()
    client.async_get_latest_vehicle_record = AsyncMock(return_value={"soc": 0})
    client.async_get_change_record = AsyncMock(
        side_effect=NioResourceNotFoundError("No recent data")
    )
    client.async_get_odometer_report = AsyncMock(
        side_effect=NioResourceNotFoundError("No recent data")
    )
    coordinator = NioDataUpdateCoordinator(hass, entry, client)

    result = await coordinator._async_update_data()

    assert result.soc_status.soc is None


async def test_three_energy_requests_then_background(hass: HomeAssistant) -> None:
    """Poll the energy window three times before one background request."""
    entry = MagicMock()
    entry.data = {CONF_VIN: "LJNABC12345678901"}
    client = MagicMock()
    client.async_get_change_record = AsyncMock(
        side_effect=NioResourceNotFoundError("No recent data")
    )
    client.async_get_latest_vehicle_record = AsyncMock(return_value={"soc": 0})
    coordinator = NioDataUpdateCoordinator(hass, entry, client)
    for _ in range(4):
        coordinator.async_set_updated_data(await coordinator._async_update_data())

    assert client.async_get_change_record.await_count == 3
    assert all(
        call.args[1] == "soc_status"
        for call in client.async_get_change_record.await_args_list
    )
    client.async_get_latest_vehicle_record.assert_awaited_once()


async def test_sparse_field_timestamps_and_duplicate_retention(
    hass: HomeAssistant,
) -> None:
    """A duplicate SoC must not refresh its source timestamp or hide fresh range."""
    entry = MagicMock()
    entry.data = {CONF_VIN: "LJNABC12345678901"}
    client = MagicMock()
    client.async_get_change_record = AsyncMock(
        side_effect=[
            {
                "soc": 50,
                "remaining_range": 278,
                "_field_timestamps": {
                    "soc": 1_760_000_000_000,
                    "remaining_range": 1_760_000_030_000,
                },
            },
            {
                "soc": 50,
                "remaining_range": 277,
                "_field_timestamps": {
                    "soc": 1_760_000_000_000,
                    "remaining_range": 1_760_000_045_000,
                },
            },
        ]
    )
    coordinator = NioDataUpdateCoordinator(hass, entry, client)
    first = await coordinator._async_update_data()
    coordinator.async_set_updated_data(first)
    second = await coordinator._async_update_data()

    assert second.soc_status.soc == 50
    assert second.soc_last_valid_at == datetime.fromtimestamp(1_760_000_000, UTC)
    assert second.soc_retained
    assert second.soc_status.remaining_range == 277
    assert second.remaining_range_last_valid_at == datetime.fromtimestamp(
        1_760_000_045, UTC
    )
    assert not second.remaining_range_retained
    assert second.telemetry["soc_status"]["soc"] == 50


async def test_optional_soc_fields_survive_sparse_events(hass: HomeAssistant) -> None:
    entry = MagicMock()
    entry.data = {CONF_VIN: "LJNABC12345678901"}
    client = MagicMock()
    client.async_get_change_record = AsyncMock(
        side_effect=[
            {
                "max_soc": 90,
                "_field_timestamps": {"max_soc": 1_760_000_000_000},
            },
            {
                "remaining_range": 278,
                "_field_timestamps": {"remaining_range": 1_760_000_030_000},
            },
        ]
    )
    coordinator = NioDataUpdateCoordinator(hass, entry, client)
    coordinator.async_set_updated_data(await coordinator._async_update_data())
    second = await coordinator._async_update_data()
    assert second.soc_status.maximum_soc == 90
    assert second.telemetry["soc_status"]["max_soc"] == 90
