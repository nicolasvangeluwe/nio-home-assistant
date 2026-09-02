"""Asynchronous client for the official NIO Open Telematics API."""

from __future__ import annotations

import logging
import re
import time
from typing import Any

from aiohttp import ClientError, ClientResponse

from homeassistant.helpers.config_entry_oauth2_flow import OAuth2Session

from .const import TELEMATICS_PATH
from .models import NioSocStatus

_LOGGER = logging.getLogger(__name__)

_SENSITIVE_KEY_PARTS = (
    "access_token",
    "authorization",
    "client_id",
    "client_secret",
    "code_verifier",
    "latitude",
    "longitude",
    "refresh_token",
    "token",
    "vin",
)
_VIN_IN_TEXT = re.compile(
    r"(?<![A-Z0-9])[A-HJ-NPR-Z0-9]{17}(?![A-Z0-9])", re.IGNORECASE
)
_SAFE_RESPONSE_HEADERS = {
    "content-type",
    "retry-after",
    "x-ratelimit-limit",
    "x-ratelimit-remaining",
    "x-ratelimit-reset",
}
_SOC_HISTORY_WINDOW_SECONDS = 24 * 60 * 60


def _redact_debug_value(value: Any, *, key: str = "") -> Any:
    """Recursively redact credentials, vehicle IDs, and precise location data."""
    normalized_key = key.casefold()
    if any(part in normalized_key for part in _SENSITIVE_KEY_PARTS):
        return "**REDACTED**"
    if isinstance(value, dict):
        return {
            str(item_key): _redact_debug_value(item_value, key=str(item_key))
            for item_key, item_value in value.items()
        }
    if isinstance(value, list):
        return [_redact_debug_value(item) for item in value]
    if isinstance(value, tuple):
        return tuple(_redact_debug_value(item) for item in value)
    if isinstance(value, str):
        return _VIN_IN_TEXT.sub("**REDACTED_VIN**", value)
    return value


def _safe_endpoint(path: str) -> str:
    """Return an endpoint path with any VIN removed."""
    return _VIN_IN_TEXT.sub("{vin}", path)


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
        """Return the newest SoC change from the last 24 hours."""
        end_time = int(time.time())
        payload = await self._async_get(
            f"{TELEMATICS_PATH}/vehicles/{vin}/soc_status/changes",
            params={
                "start_time": end_time - _SOC_HISTORY_WINDOW_SECONDS,
                "end_time": end_time,
            },
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
        statuses = [
            NioSocStatus.from_payload(item)
            for item in sorted(
                records,
                key=lambda item: item.get("sample_timestamp", 0),
                reverse=True,
            )
        ]
        return NioSocStatus.merge(*statuses)

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
            _LOGGER.debug(
                "NIO API trace: endpoint=%s stage=transport error_type=%s",
                _safe_endpoint(path),
                type(err).__name__,
            )
            raise NioApiError("Unable to reach the NIO API") from err
        payload: Any = None
        json_error: Exception | None = None
        try:
            payload = await response.json()
        except (ClientError, ValueError) as err:
            json_error = err

        safe_headers = {
            key: value
            for key, value in response.headers.items()
            if key.casefold() in _SAFE_RESPONSE_HEADERS
        }
        _LOGGER.debug(
            "NIO API trace: endpoint=%s params=%s http_status=%s headers=%s "
            "payload=%s json_error=%s",
            _safe_endpoint(path),
            _redact_debug_value(params),
            response.status,
            safe_headers,
            _redact_debug_value(payload),
            type(json_error).__name__ if json_error else None,
        )

        await self._raise_for_status(response)
        if json_error is not None:
            raise NioApiError("NIO returned a non-JSON response") from json_error
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
