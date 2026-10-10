"""Asynchronous client for the official NIO Open Telematics API."""

from __future__ import annotations

import logging
import re
import time
from datetime import UTC, datetime
from email.utils import parsedate_to_datetime
from typing import Any

from aiohttp import ClientError, ClientResponse
from homeassistant.helpers.config_entry_oauth2_flow import (
    OAuth2Session,
    OAuth2TokenRequestError,
    OAuth2TokenRequestReauthError,
    OAuth2TokenRequestTransientError,
)

from .const import TELEMATICS_PATH
from .models import NioSocStatus
from .pacing import NioRequestPacer

_LOGGER = logging.getLogger(__name__)

_SENSITIVE_KEY_PARTS = (
    "access_token",
    "authorization",
    "btry_pak_sn",
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
_MILLISECONDS_PER_SECOND = 1_000
_ENERGY_WINDOW_SECONDS = 10 * 60
_RATE_LIMIT_MARKER = re.compile(
    r"rate[_ -]?limit|too[_ -]?many|throttl|request[_ -]?frequen",
    re.IGNORECASE,
)
_SOC_WINDOW_CANDIDATES_SECONDS = (
    12 * 60 * 60,
    6 * 60 * 60,
    3 * 60 * 60,
    60 * 60,
    30 * 60,
    10 * 60,
)


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
    """NIO denied access to a telemetry resource."""


class NioInvalidParameterError(NioApiError):
    """NIO rejected a documented request parameter."""


class NioResourceNotFoundError(NioApiError):
    """NIO has no accessible record for the requested resource."""


class NioRateLimitError(NioApiError):
    """NIO rate limited the request."""

    def __init__(self, retry_after: float | None) -> None:
        super().__init__("NIO API rate limit exceeded")
        self.retry_after = retry_after


class NioApiClient:
    """Minimal read-only NIO API client."""

    def __init__(
        self,
        oauth_session: OAuth2Session,
        base_url: str,
        pacer: NioRequestPacer | None = None,
    ) -> None:
        self._oauth_session = oauth_session
        self._base_url = base_url.rstrip("/")
        self._soc_window_seconds: int | None = None
        self._pacer = pacer

    async def async_get_soc_status(
        self,
        vin: str,
    ) -> NioSocStatus:
        """Return the newest SoC change from NIO's largest accepted window."""
        end_seconds = int(time.time())
        path = f"{TELEMATICS_PATH}/vehicles/{vin}/soc_status/changes"
        windows = (
            (self._soc_window_seconds,)
            if self._soc_window_seconds is not None
            else _SOC_WINDOW_CANDIDATES_SECONDS
        )
        last_error: NioInvalidParameterError | None = None
        for window_seconds in windows:
            end_milliseconds = end_seconds * _MILLISECONDS_PER_SECOND
            try:
                payload = await self._async_get(
                    path,
                    params={
                        "start_time": (
                            end_milliseconds - window_seconds * _MILLISECONDS_PER_SECOND
                        ),
                        "end_time": end_milliseconds,
                    },
                )
            except NioInvalidParameterError as err:
                last_error = err
                continue
            except NioResourceNotFoundError:
                self._soc_window_seconds = window_seconds
                raise
            self._soc_window_seconds = window_seconds
            break
        else:
            if last_error is not None:
                raise last_error
            raise NioApiError("NIO did not accept a SoC query window")
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

    async def async_get_change_record(self, vin: str, resource: str) -> dict[str, Any]:
        """Return the newest record from a documented change endpoint."""
        params = None
        if resource == "soc_status":
            end = int(time.time() * _MILLISECONDS_PER_SECOND)
            params = {
                "start_time": end - _ENERGY_WINDOW_SECONDS * _MILLISECONDS_PER_SECOND,
                "end_time": end,
            }
        payload = await self._async_get(
            f"{TELEMATICS_PATH}/vehicles/{vin}/{resource}/changes",
            params=params,
        )
        data = payload.get("data")
        if not isinstance(data, list) or not data:
            raise NioResourceNotFoundError("NIO returned no telemetry records")
        records = [item for item in data if isinstance(item, dict)]
        if not records:
            raise NioApiError("NIO returned an invalid telemetry payload")
        if resource == "soc_status":
            # NIO may emit separate sparse changes for different energy fields.
            # Keep the newest non-null value of each field in this window.
            merged: dict[str, Any] = {}
            field_timestamps: dict[str, Any] = {}
            for record in sorted(
                records, key=lambda item: item.get("sample_timestamp", 0)
            ):
                for key, value in record.items():
                    if value is not None and (
                        key not in {"soc", "remaining_range"}
                        or getattr(NioSocStatus.from_payload({key: value}), key)
                        is not None
                    ):
                        merged[key] = value
                        if key != "sample_timestamp":
                            field_timestamps[key] = record.get("sample_timestamp")
            merged["_field_timestamps"] = field_timestamps
            return merged
        return max(records, key=lambda item: item.get("sample_timestamp", 0))

    async def async_get_latest_vehicle_record(self, vin: str) -> dict[str, Any]:
        """Return the unmodified latest vehicle-status record."""
        payload = await self._async_get(
            f"{TELEMATICS_PATH}/vehicles/{vin}/vehicle_status/latest"
        )
        data = payload.get("data")
        if not isinstance(data, dict):
            raise NioApiError("NIO returned an invalid vehicle status payload")
        return data

    async def async_get_odometer_report(self, vin: str) -> dict[str, Any]:
        """Return the newest documented aftersales odometer report."""
        payload = await self._async_get(
            f"{TELEMATICS_PATH}/aftersales/vehicles/{vin}/odometer_reports"
        )
        data = payload.get("data")
        if not isinstance(data, list) or not data:
            raise NioResourceNotFoundError("NIO returned no odometer reports")
        records = [item for item in data if isinstance(item, dict)]
        if not records:
            raise NioApiError("NIO returned an invalid odometer payload")
        return max(records, key=lambda item: str(item.get("recorded_at", "")))

    async def async_get_latest_vehicle_status(self, vin: str) -> NioSocStatus:
        """Return the latest overall vehicle status snapshot."""
        data = await self.async_get_latest_vehicle_record(vin)
        _LOGGER.debug("NIO latest vehicle response fields: %s", sorted(data))
        return NioSocStatus.from_payload(data)

    async def _async_get(
        self, path: str, *, params: dict[str, int] | None = None
    ) -> dict[str, Any]:
        request_kwargs: dict[str, Any] = {"headers": {"Accept": "application/json"}}
        if params is not None:
            request_kwargs["params"] = params
        try:
            if self._pacer is not None:
                await self._pacer.wait()
            response = await self._oauth_session.async_request(
                "GET",
                f"{self._base_url}{path}",
                **request_kwargs,
            )
        except OAuth2TokenRequestReauthError:
            # HA's OAuth2Session starts the native reauth flow for this error.
            raise
        except OAuth2TokenRequestTransientError as err:
            raise NioApiError(
                "NIO OAuth token service is temporarily unavailable"
            ) from err
        except OAuth2TokenRequestError as err:
            raise NioApiError("NIO OAuth token request failed") from err
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

        try:
            await self._raise_for_status(response, payload)
        except NioRateLimitError as err:
            if self._pacer is not None:
                await self._pacer.rate_limited(err.retry_after)
            raise
        if json_error is not None:
            raise NioApiError("NIO returned a non-JSON response") from json_error
        if not isinstance(payload, dict):
            raise NioApiError("NIO returned an invalid response envelope")
        result_code = payload.get("result_code")
        if _is_rate_limited(payload):
            retry_after = _retry_after(response.headers)
            if self._pacer is not None:
                await self._pacer.rate_limited(retry_after)
            raise NioRateLimitError(retry_after)
        if result_code == "access_denied":
            raise NioPermissionError("NIO denied access to this telemetry resource")
        if result_code == "resource_not_found":
            raise NioResourceNotFoundError("NIO resource was not found")
        if result_code == "invalid_param":
            raise NioInvalidParameterError("NIO rejected request parameters")
        if result_code != "success":
            raise NioApiError(
                f"NIO request failed: {payload.get('result_code', 'unknown')}"
            )
        if self._pacer is not None:
            self._pacer.succeeded()
        return payload

    @staticmethod
    async def _raise_for_status(response: ClientResponse, payload: Any = None) -> None:
        if response.status == 401:
            raise NioAuthenticationError("NIO access token is invalid or expired")
        if response.status == 429 or (
            response.status == 403 and _is_rate_limited(payload)
        ):
            raise NioRateLimitError(_retry_after(response.headers))
        if response.status == 403:
            raise NioPermissionError("NIO denied access to this telemetry resource")
        if response.status in (400, 404) and isinstance(payload, dict):
            result_code = payload.get("result_code")
            if result_code == "invalid_param":
                raise NioInvalidParameterError("NIO rejected request parameters")
            if result_code == "resource_not_found":
                raise NioResourceNotFoundError("NIO resource was not found")
            if result_code == "access_denied":
                raise NioPermissionError("NIO denied access to this telemetry resource")
        if response.status >= 400:
            raise NioApiError(f"NIO API returned HTTP {response.status}")


def _is_rate_limited(payload: Any) -> bool:
    if not isinstance(payload, dict):
        return False
    return any(
        _RATE_LIMIT_MARKER.search(str(payload.get(key) or ""))
        for key in ("result_code", "display_msg", "debug_msg")
    )


def _retry_after(headers: Any) -> float | None:
    raw = headers.get("Retry-After") or headers.get("retry-after")
    if not raw:
        return None
    try:
        return max(0.0, float(raw))
    except (TypeError, ValueError):
        try:
            date = parsedate_to_datetime(raw)
            return max(0.0, (date - datetime.now(UTC)).total_seconds())
        except (TypeError, ValueError, OverflowError):
            return None
