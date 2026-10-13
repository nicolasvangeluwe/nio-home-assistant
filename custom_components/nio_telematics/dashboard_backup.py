"""Versioned, credential-free backup format for the optional vehicle dashboard."""

from __future__ import annotations

import json
from copy import deepcopy
from datetime import UTC, datetime
from hashlib import sha256

FORMAT = "nio-telematics-dashboard"
VERSION = 1
MAX_BYTES = 8 * 1024 * 1024
FORBIDDEN_KEYS = {
    "access_token",
    "refresh_token",
    "client_secret",
    "api_key",
    "authorization",
    "password",
    "token",
    "vin",
}
HISTORY_COLLECTIONS = {
    "trips": list,
    "charges": dict,
    "samples": list,
    "counters": list,
    "parked_losses": list,
    "source_transitions": list,
    "native_replays": dict,
}


def vehicle_fingerprint(vin: str) -> str:
    """Identify the destination vehicle without exporting its VIN."""
    return sha256(vin.encode("utf-8")).hexdigest()


def _check_safe(value: object) -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            if not isinstance(key, str) or key.lower() in FORBIDDEN_KEYS:
                raise ValueError("Backup contains a credential or vehicle identifier")
            _check_safe(item)
    elif isinstance(value, list):
        for item in value:
            _check_safe(item)


def validate_history(history: object) -> dict | None:
    """Reject malformed archives before any HA Store or entry is changed."""
    if history is None:
        return None
    if not isinstance(history, dict):
        raise ValueError("History must be an object")
    for key, expected in HISTORY_COLLECTIONS.items():
        if key not in history or not isinstance(history[key], expected):
            raise ValueError(f"History is missing a valid {key} collection")
    if type(history.get("revision")) is not int or history["revision"] < 0:
        raise ValueError("History revision is invalid")
    if not isinstance(history.get("preferences"), dict):
        raise ValueError("History preferences are invalid")
    for key in ("last", "active", "opening"):
        if history.get(key) is not None and not isinstance(history[key], dict):
            raise ValueError(f"History {key} is invalid")
    if any(not isinstance(row, dict) for row in history["trips"]):
        raise ValueError("Trip history contains an invalid record")
    if any(not isinstance(row, dict) for row in history["samples"]):
        raise ValueError("Sample history contains an invalid record")
    if any(not isinstance(row, dict) for row in history["charges"].values()):
        raise ValueError("Charging history contains an invalid record")
    _check_safe(history)
    return deepcopy(history)


def make_backup(vin: str, preferences: dict, history: dict | None) -> dict:
    """Build a portable archive containing no NIO authorization material."""
    result = {
        "format": FORMAT,
        "version": VERSION,
        "exported_at": datetime.now(UTC).isoformat(),
        "vehicle_fingerprint": vehicle_fingerprint(vin),
        "preferences": deepcopy(preferences),
        "history": validate_history(history),
    }
    _check_safe(result)
    if len(json.dumps(result, ensure_ascii=False).encode("utf-8")) > MAX_BYTES:
        raise ValueError("Backup exceeds the 8 MB transfer limit")
    return result


def parse_backup(value: object, vin: str) -> tuple[dict, dict | None]:
    """Validate archive identity and shape; caller validates HA entity IDs."""
    if not isinstance(value, dict) or set(value) != {
        "format",
        "version",
        "exported_at",
        "vehicle_fingerprint",
        "preferences",
        "history",
    }:
        raise ValueError("Not a supported NIO dashboard backup")
    if (
        value["format"] != FORMAT
        or type(value["version"]) is not int
        or value["version"] != VERSION
    ):
        raise ValueError("Unsupported NIO dashboard backup version")
    if value["vehicle_fingerprint"] != vehicle_fingerprint(vin):
        raise ValueError("This backup belongs to a different vehicle")
    if not isinstance(value["exported_at"], str):
        raise ValueError("Backup date is invalid")
    try:
        datetime.fromisoformat(value["exported_at"])
    except ValueError as err:
        raise ValueError("Backup date is invalid") from err
    if not isinstance(value["preferences"], dict):
        raise ValueError("Dashboard preferences are invalid")
    if len(json.dumps(value, ensure_ascii=False).encode("utf-8")) > MAX_BYTES:
        raise ValueError("Backup exceeds the 8 MB transfer limit")
    _check_safe(value)
    return deepcopy(value["preferences"]), validate_history(value["history"])


def history_summary(history: dict | None) -> dict:
    """Small human-facing preview, not a copy of private trip data."""
    if history is None:
        return {"trips": 0, "charges": 0, "samples": 0, "revision": None}
    return {
        "trips": len(history["trips"]),
        "charges": len(history["charges"]),
        "samples": len(history["samples"]),
        "revision": history["revision"],
    }
