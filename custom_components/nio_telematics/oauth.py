"""NIO-specific OAuth response helpers."""

from __future__ import annotations

from typing import Any


class InvalidTokenResponseError(ValueError):
    """The NIO OAuth response did not contain a usable token."""


def unwrap_token_response(payload: dict[str, Any]) -> dict[str, Any]:
    """Extract and validate NIO's OAuth token from its API envelope."""
    if payload.get("result_code") != "success":
        raise InvalidTokenResponseError(
            f"NIO OAuth failed: {payload.get('result_code', 'unknown')}"
        )
    token = payload.get("data")
    if not isinstance(token, dict):
        raise InvalidTokenResponseError("NIO OAuth response has no data object")
    required = ("access_token", "refresh_token", "expires_in", "token_type")
    if any(not token.get(key) for key in required):
        raise InvalidTokenResponseError("NIO OAuth response is missing token fields")
    return dict(token)
