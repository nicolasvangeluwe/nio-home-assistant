"""API-client tests for NIO Open Telematics."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from custom_components.nio_telematics.api import (
    NioApiClient,
    NioAuthenticationError,
    NioPermissionError,
    NioRateLimitError,
    NioResourceNotFoundError,
)
from custom_components.nio_telematics.const import API_BASE_URL


def response(status: int, payload: dict, headers: dict | None = None) -> MagicMock:
    """Build a minimal aiohttp response double."""
    result = MagicMock(status=status, headers=headers or {})
    result.json = AsyncMock(return_value=payload)
    return result


async def test_soc_request_uses_oauth_session_and_newest_record() -> None:
    oauth_session = MagicMock()
    oauth_session.async_request = AsyncMock(
        return_value=response(
            200,
            {
                "result_code": "success",
                "data": [
                    {
                        "soc": 40,
                        "remaining_range": 204.5,
                        "chrg_final_soc": 80,
                        "sample_timestamp": 1_760_000_000_000,
                    },
                    {"soc": 41, "sample_timestamp": 1_760_000_100_000},
                ],
            },
        )
    )
    client = NioApiClient(oauth_session, API_BASE_URL)

    status = await client.async_get_soc_status("LJNABC12345678901")

    assert status.soc == 41
    assert status.remaining_range == 204.5
    assert status.charging_target == 80
    request = oauth_session.async_request.await_args
    assert request.args[0] == "GET"
    assert request.args[1].endswith(
        "/vehicles/LJNABC12345678901/soc_status/changes"
    )
    assert "params" not in request.kwargs
    assert "Authorization" not in request.kwargs["headers"]


async def test_latest_vehicle_status_uses_snapshot_endpoint() -> None:
    oauth_session = MagicMock()
    oauth_session.async_request = AsyncMock(
        return_value=response(
            200,
            {
                "result_code": "success",
                "data": {
                    "soc": 52,
                    "chrg_state": "3",
                    "sample_timestamp": 1_760_000_100_000,
                },
            },
        )
    )
    client = NioApiClient(oauth_session, API_BASE_URL)

    status = await client.async_get_latest_vehicle_status("LJNABC12345678901")

    assert status.soc == 52
    request = oauth_session.async_request.await_args
    assert request.args[1].endswith(
        "/vehicles/LJNABC12345678901/vehicle_status/latest"
    )


async def test_resource_not_found_is_mapped() -> None:
    oauth_session = MagicMock()
    oauth_session.async_request = AsyncMock(
        return_value=response(200, {"result_code": "resource_not_found"})
    )
    client = NioApiClient(oauth_session, API_BASE_URL)

    with pytest.raises(NioResourceNotFoundError):
        await client.async_get_soc_status("LJNABC12345678901")


async def test_envelope_access_denied_is_mapped() -> None:
    oauth_session = MagicMock()
    oauth_session.async_request = AsyncMock(
        return_value=response(200, {"result_code": "access_denied"})
    )
    client = NioApiClient(oauth_session, API_BASE_URL)

    with pytest.raises(NioPermissionError):
        await client.async_get_latest_vehicle_status("LJNABC12345678901")


@pytest.mark.parametrize(
    ("status", "headers", "error"),
    [
        (401, {}, NioAuthenticationError),
        (403, {}, NioPermissionError),
        (429, {"Retry-After": "30"}, NioRateLimitError),
    ],
)
async def test_http_errors_are_mapped(status, headers, error) -> None:
    oauth_session = MagicMock()
    oauth_session.async_request = AsyncMock(
        return_value=response(status, {}, headers)
    )
    client = NioApiClient(oauth_session, API_BASE_URL)
    with pytest.raises(error):
        await client.async_get_soc_status("LJNABC12345678901")
