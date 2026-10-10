"""Bound and redact telemetry shown in Home Assistant diagnostics."""

from __future__ import annotations

import json
import re
from typing import Any

MAX_DIAGNOSTIC_ATTRIBUTE_BYTES = 12_000
MAX_DIAGNOSTIC_LIST_ITEMS = 50
MAX_DIAGNOSTIC_NESTING = 8

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
    "url",
    "uuid",
    "vin",
)
_VIN_IN_TEXT = re.compile(
    r"(?<![A-Z0-9])[A-HJ-NPR-Z0-9]{17}(?![A-Z0-9])", re.IGNORECASE
)


def _redact(value: Any, *, key: str = "", depth: int = 0) -> Any:
    """Limit nested data and remove identifiers, locations and signed URLs."""
    normalized_key = key.casefold()
    if normalized_key in {"lat", "lon", "lng"} or any(
        part in normalized_key for part in _SENSITIVE_KEY_PARTS
    ):
        return "**REDACTED**"
    if isinstance(value, dict):
        if depth >= MAX_DIAGNOSTIC_NESTING:
            return {}
        return {
            str(item_key): _redact(item_value, key=str(item_key), depth=depth + 1)
            for item_key, item_value in value.items()
        }
    if isinstance(value, (list, tuple)):
        if depth >= MAX_DIAGNOSTIC_NESTING:
            return []
        return [
            _redact(item, depth=depth + 1) for item in value[:MAX_DIAGNOSTIC_LIST_ITEMS]
        ]
    if isinstance(value, str):
        return _VIN_IN_TEXT.sub("**REDACTED_VIN**", value)
    return value


def safe_diagnostic_attributes(value: Any) -> dict[str, Any]:
    """Return a bounded, JSON-safe diagnostic attribute mapping."""
    redacted = _redact(value)
    attributes = redacted if isinstance(redacted, dict) else {"value": redacted}
    try:
        encoded = json.dumps(attributes, ensure_ascii=False, separators=(",", ":"))
    except (TypeError, ValueError):
        return {"payload_truncated": True}
    if len(encoded.encode()) > MAX_DIAGNOSTIC_ATTRIBUTE_BYTES:
        return {"payload_truncated": True}
    return attributes
