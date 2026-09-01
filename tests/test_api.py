"""API-client tests for NIO Open Telematics."""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from custom_components.nio_telematics.api import (
    NioApiClient,
    NioAuthenticationError,
    NioPermissionError,
    NioRateLimitError,
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
                    {"soc": 40, "event_time": 1_760_000_000},
                    {"soc": 41, "event_time": 1_760_000_100},
                ],
            },
        )
    )
    client = NioApiClient(oauth_session, API_BASE_URL)

    status = await client.async_get_soc_status(
        "LJNABC12345678901", now=datetime(2026, 9, 1, tzinfo=UTC)
    )

    assert status.soc == 41
    request = oauth_session.async_request.await_args
    assert request.args[0] == "GET"
    assert request.args[1].endswith(
        "/vehicles/LJNABC12345678901/soc_status/changes"
    )
    assert "Authorization" not in request.kwargs["headers"]


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
