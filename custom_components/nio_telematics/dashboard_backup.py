"""Versioned, credential-free backup format for the optional vehicle dashboard."""

from __future__ import annotations

import json
from copy import deepcopy
from datetime import UTC, datetime
from hashlib import sha256
from math import isfinite
from re import fullmatch

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
    _validate_native_zero_capture(history.get("native_zero_capture"))
    _validate_pending_epoch(history.get("pending_epoch"))
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
    # Legacy archives intentionally omit this discriminator and retain EUR
    # semantics when loaded. Explicit metadata must never be malformed.
    for row in [history["preferences"], *history["charges"].values()]:
        if "currency" in row and (
            not isinstance(row["currency"], str)
            or not fullmatch(r"[A-Z]{3}", row["currency"])
        ):
            raise ValueError("History currency is invalid")
    resolutions = history.get("gap_resolutions", {})
    paths = history.get("parking_source_paths", [])
    if not isinstance(paths, list):
        raise ValueError("Parking source paths must be a list")
    for path in paths:
        if not isinstance(path, list) or not path:
            raise ValueError("Invalid parking source path")
        previous = None
        for point in path:
            if (
                not isinstance(point, dict)
                or any(
                    isinstance(point.get(key), bool)
                    or not isinstance(point.get(key), (int, float))
                    or not isfinite(point[key])
                    for key in ("t", "odo", "energy")
                )
                or point["odo"] <= 0
                or point["energy"] < 0
                or point.get("energy_source") != "native_soc"
                or not isinstance(point.get("home_connected"), bool)
                or (
                    "until" in point
                    and (
                        isinstance(point["until"], bool)
                        or not isinstance(point["until"], (int, float))
                        or not isfinite(point["until"])
                        or point["until"] < point["t"]
                    )
                )
                or (
                    "capacity_kwh" in point
                    and (
                        isinstance(point["capacity_kwh"], bool)
                        or not isinstance(point["capacity_kwh"], (int, float))
                        or not isfinite(point["capacity_kwh"])
                        or point["capacity_kwh"] <= 0
                    )
                )
                or (previous is not None and point["t"] <= previous)
            ):
                raise ValueError("Invalid parking source path")
            previous = point.get("until", point["t"])
    if not isinstance(resolutions, dict):
        raise ValueError("Gap resolutions must be an object")
    for ident, row in resolutions.items():
        if (
            not isinstance(ident, str)
            or not fullmatch(r"gap-[a-f0-9]{24}", ident)
            or not isinstance(row, dict)
            or not isinstance(row.get("fingerprint"), str)
            or not fullmatch(r"[a-f0-9]{64}", row["fingerprint"])
            or row.get("status") not in ("manual", "ignored")
        ):
            raise ValueError("Invalid gap resolution")
        if row["status"] == "ignored":
            if set(row) != {"fingerprint", "status"}:
                raise ValueError("Ignored gap cannot contain manual usage")
            continue
        if set(row) != {"fingerprint", "status", "energy_kwh", "cost", "currency"}:
            raise ValueError("Invalid manual gap resolution")
        energy, cost = row["energy_kwh"], row["cost"]
        if (
            isinstance(energy, bool)
            or not isinstance(energy, (int, float))
            or not isfinite(energy)
            or energy < 0
            or (
                cost is not None
                and (
                    isinstance(cost, bool)
                    or not isinstance(cost, (int, float))
                    or not isfinite(cost)
                )
            )
            or not isinstance(row["currency"], str)
            or not fullmatch(r"[A-Z]{3}", row["currency"])
        ):
            raise ValueError("Invalid manual gap amount or currency")
    errors = history.get("measurement_errors", {})
    if not isinstance(errors, dict):
        raise ValueError("Measurement errors must be an object")
    for ident, row in errors.items():
        if (
            not isinstance(ident, str)
            or not fullmatch(r"loss-[a-f0-9]{24}", ident)
            or not isinstance(row, dict)
            or set(row)
            != {
                "fingerprint",
                "start",
                "end",
                "kwh",
                "paired_candidate_id",
                "paired_candidate_fingerprint",
            }
            or not isinstance(row["fingerprint"], str)
            or not fullmatch(r"[a-f0-9]{64}", row["fingerprint"])
            or any(
                isinstance(row[key], bool)
                or not isinstance(row[key], (int, float))
                or not isfinite(row[key])
                for key in ("start", "end", "kwh")
            )
            or row["start"] > row["end"]
            or row["kwh"] < 0
            or (
                row["paired_candidate_id"] is not None
                and not isinstance(row["paired_candidate_id"], str)
            )
            or (
                row["paired_candidate_fingerprint"] is not None
                and (
                    not isinstance(row["paired_candidate_fingerprint"], str)
                    or not fullmatch(
                        r"[a-f0-9]{64}", row["paired_candidate_fingerprint"]
                    )
                )
            )
            or (row["paired_candidate_id"] is None)
            != (row["paired_candidate_fingerprint"] is None)
        ):
            raise ValueError("Invalid measurement error")
    _check_safe(history)
    return deepcopy(history)


def _validate_pending_epoch(epoch):
    """An old-calibration reading is bounded validation context, never new stock."""
    if epoch is None:
        return
    if (
        not isinstance(epoch, dict)
        or set(epoch)
        not in (
            {"capacity_kwh", "full_range_km"},
            {"capacity_kwh", "full_range_km", "native_validation_baseline"},
        )
        or any(
            isinstance(epoch.get(key), bool)
            or not isinstance(epoch.get(key), (int, float))
            or not isfinite(epoch[key])
            or epoch[key] <= 0
            for key in ("capacity_kwh", "full_range_km")
        )
    ):
        raise ValueError("Invalid pending energy epoch")
    if "native_validation_baseline" not in epoch:
        return
    context = epoch["native_validation_baseline"]
    if not isinstance(context, dict) or set(context) != {"capacity_kwh", "sample"}:
        raise ValueError("Invalid native validation baseline")
    # Reuse precisely the same accepted-native baseline validation. These
    # temporary fields are validation scaffolding, not imported source data.
    _validate_native_zero_capture(
        {
            "source": "direct",
            "capacity_kwh": context["capacity_kwh"],
            "baseline": context["sample"],
            "latest": {key: context["sample"].get(key) for key in ("t", "odo")}
            if isinstance(context["sample"], dict)
            else {},
            "started": None,
            "soc_at": 0,
            "range_at": 0,
            "released": False,
            "accepted_soc": None,
            "accepted_soc_at": None,
            "needs_advanced": False,
        }
    )


def _validate_native_zero_capture(guard):
    """Validate the one bounded restart-capture record, including held distance."""
    if guard is None:
        return

    def finite(value):
        return (
            not isinstance(value, bool)
            and isinstance(value, (int, float))
            and isfinite(value)
        )

    if not isinstance(guard, dict) or set(guard) != {
        "source",
        "capacity_kwh",
        "baseline",
        "latest",
        "started",
        "soc_at",
        "range_at",
        "released",
        "accepted_soc",
        "accepted_soc_at",
        "needs_advanced",
    }:
        raise ValueError("Invalid native zero capture")
    baseline, latest = guard["baseline"], guard["latest"]
    if (
        not isinstance(guard["source"], str)
        or not fullmatch(r"direct|companion:(?:[0-9]+|None)", guard["source"])
        or not finite(guard["capacity_kwh"])
        or guard["capacity_kwh"] <= 0
        or not isinstance(baseline, dict)
        or set(baseline) != {"t", "odo", "soc", "energy"}
        or not all(finite(value) for value in baseline.values())
        or baseline["t"] < 0
        or baseline["odo"] <= 0
        or not 1 < baseline["soc"] <= 100
        or not 0 < baseline["energy"] <= guard["capacity_kwh"]
        or abs(baseline["energy"] - baseline["soc"] / 100 * guard["capacity_kwh"])
        > 1e-6
        or not isinstance(latest, dict)
        or set(latest) != {"t", "odo"}
        or not all(finite(value) for value in latest.values())
        or latest["t"] < baseline["t"]
        or latest["odo"] < baseline["odo"]
        or latest["odo"] - baseline["odo"]
        > (latest["t"] - baseline["t"]) / 3600 * 250 + 5
        or (
            guard["started"] is not None
            and (not finite(guard["started"]) or guard["started"] < 0)
        )
        or not all(
            finite(guard[key]) and guard[key] >= 0 for key in ("soc_at", "range_at")
        )
        or not isinstance(guard["released"], bool)
        or not isinstance(guard["needs_advanced"], bool)
    ):
        raise ValueError("Invalid native zero capture")
    if guard["released"]:
        if (
            not finite(guard["accepted_soc"])
            or not 0 <= guard["accepted_soc"] <= 100
            or not finite(guard["accepted_soc_at"])
            or guard["accepted_soc_at"] < 0
        ):
            raise ValueError("Invalid native zero capture release")
    elif guard["accepted_soc"] is not None or guard["accepted_soc_at"] is not None:
        raise ValueError("Invalid native zero capture release")


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
