"""Asynchronous client for the official NIO Open Telematics API."""

from __future__ import annotations

import logging
from typing import Any

from aiohttp import ClientError, ClientResponse

from homeassistant.helpers.config_entry_oauth2_flow import OAuth2Session

from .const import TELEMATICS_PATH
from .models import NioSocStatus

_LOGGER = logging.getLogger(__name__)


class NioApiError(Exception):
    """Base NIO API error."""


class NioAuthenticationError(NioApiError):
    """NIO rejected or expired the access token."""


class NioPermissionError(NioApiError):
    """The OAuth grant lacks a required scope."""


class NioResourceNotFoundError(NioApiError):
    """NIO has no accessible record for the requested resource."""


class NioRateLimitError(NioApiError):
    """NIO rate limited the request."""

    def __init__(self, retry_after: int | None) -> None:
        super().__init__("NIO API rate limit exceeded")
        self.retry_after = retry_after


class NioApiClient:
    """Minimal read-only NIO API client."""

    def __init__(
        self,
        oauth_session: OAuth2Session,
        base_url: str,
    ) -> None:
        self._oauth_session = oauth_session
        self._base_url = base_url.rstrip("/")

    async def async_get_soc_status(
        self,
        vin: str,
    ) -> NioSocStatus:
        """Return the newest SoC change for a vehicle."""
        payload = await self._async_get(
            f"{TELEMATICS_PATH}/vehicles/{vin}/soc_status/changes",
        )
        data = payload.get("data")
        if not isinstance(data, list) or not data:
            raise NioApiError("NIO returned no SoC status records")
        records = [item for item in data if isinstance(item, dict)]
        if not records:
            raise NioApiError("NIO returned an invalid SoC status payload")
        _LOGGER.debug(
            "NIO SoC change response shape: record_count=%d field_sets=%s",
            len(records),
            [sorted(item) for item in records[:10]],
        )
        latest = max(records, key=lambda item: item.get("sample_timestamp", 0))
        return NioSocStatus.from_payload(latest)

    async def async_get_latest_vehicle_status(self, vin: str) -> NioSocStatus:
        """Return the latest overall vehicle status snapshot."""
        payload = await self._async_get(
            f"{TELEMATICS_PATH}/vehicles/{vin}/vehicle_status/latest"
        )
        data = payload.get("data")
        if not isinstance(data, dict):
            raise NioApiError("NIO returned an invalid vehicle status payload")
        _LOGGER.debug("NIO latest vehicle response fields: %s", sorted(data))
        return NioSocStatus.from_payload(data)

    async def _async_get(
        self, path: str, *, params: dict[str, int] | None = None
    ) -> dict[str, Any]:
        request_kwargs: dict[str, Any] = {
            "headers": {"Accept": "application/json"}
        }
        if params is not None:
            request_kwargs["params"] = params
        try:
            response = await self._oauth_session.async_request(
                "GET",
                f"{self._base_url}{path}",
                **request_kwargs,
            )
        except ClientError as err:
            raise NioApiError("Unable to reach the NIO API") from err
        await self._raise_for_status(response)
        try:
            payload = await response.json()
        except (ClientError, ValueError) as err:
            raise NioApiError("NIO returned a non-JSON response") from err
        if not isinstance(payload, dict):
            raise NioApiError("NIO returned an invalid response envelope")
        result_code = payload.get("result_code")
        if result_code == "access_denied":
            raise NioPermissionError("NIO OAuth grant lacks the required scope")
        if result_code == "resource_not_found":
            raise NioResourceNotFoundError("NIO resource was not found")
        if result_code != "success":
            raise NioApiError(
                f"NIO request failed: {payload.get('result_code', 'unknown')}"
            )
        return payload

    @staticmethod
    async def _raise_for_status(response: ClientResponse) -> None:
        if response.status == 401:
            raise NioAuthenticationError("NIO access token is invalid or expired")
        if response.status == 403:
            raise NioPermissionError("NIO OAuth grant lacks the required scope")
        if response.status == 429:
            raw_retry_after = response.headers.get("Retry-After")
            retry_after = int(raw_retry_after) if raw_retry_after and raw_retry_after.isdigit() else None
            raise NioRateLimitError(retry_after)
        if response.status >= 400:
            raise NioApiError(f"NIO API returned HTTP {response.status}")
