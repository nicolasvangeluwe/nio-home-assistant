"""Bounded contract tests; no backend or live Home Assistant connection."""

from copy import deepcopy

import pytest

from custom_components.nio_telematics.companion_snapshot import (
    CompanionContractError,
    classify_companion_error,
    parse_companion_snapshot,
)

NOW = "2026-10-20T19:00:00.000Z"
SAMPLE = "2026-10-20T18:59:07.321Z"


def _field(
    value: float | str | None,
    unit: str | None,
    endpoint: str | None,
    *,
    quality: str = "valid",
    reason: str | None = None,
) -> dict:
    return {
        "value": value,
        "unit": unit,
        "sourceTimestamp": SAMPLE if endpoint else None,
        "receivedAt": "2026-10-20T18:59:09.000Z" if endpoint else None,
        "quality": quality,
        "reason": reason,
        "sourceEndpoint": endpoint,
    }


def _snapshot() -> dict:
    return {
        "schemaVersion": 1,
        "vehicleKey": "a" * 64,
        "identity": {"vin": "A" * 17, "ownership": "verified"},
        "source": "nio_official",
        "synthetic": False,
        "sourceGeneration": 1,
        "snapshotAt": NOW,
        "capabilities": {
            "readOnly": True,
            "location": False,
            "controls": False,
            "history": False,
        },
        "fields": {
            "socPercent": _field(48.5, "%", "soc_status"),
            "targetSocPercent": _field(
                None, "%", None, quality="unavailable", reason="not_reported"
            ),
            "maximumSocPercent": _field(90, "%", "soc_status"),
            "batteryCurrentA": _field(0.4, "A", "soc_status"),
            "vehicleState": _field("PARKED_VEHICLE", None, "vehicle_status"),
            "energyChargingState": _field("NO_CHARGING", None, "soc_status"),
            "dynamicsChargingState": _field("NOT_CHARGING", None, "vehicle_status"),
            "rangeKm": _field(
                None,
                "km",
                "soc_status",
                quality="unavailable",
                reason="unit_unverified",
            ),
            "odometerKm": _field(
                None,
                "km",
                "vehicle_status",
                quality="unavailable",
                reason="unit_unverified",
            ),
        },
    }


def test_valid_snapshot_keeps_field_provenance_and_withholds_unverified_units() -> None:
    snapshot = parse_companion_snapshot(_snapshot())
    assert snapshot.vin == "A" * 17
    assert snapshot.usable_value("socPercent") == 48.5
    assert snapshot.usable_value("maximumSocPercent") == 90.0
    assert snapshot.usable_value("rangeKm") is None
    assert snapshot.usable_value("odometerKm") is None
    assert snapshot.fields["socPercent"].source_timestamp.isoformat() == (
        "2026-10-20T18:59:07.321000+00:00"
    )


def test_zero_soc_is_valid_only_from_energy_endpoint() -> None:
    payload = _snapshot()
    payload["fields"]["socPercent"]["value"] = 0
    assert parse_companion_snapshot(payload).usable_value("socPercent") == 0.0
    payload["fields"]["socPercent"]["sourceEndpoint"] = "vehicle_status"
    with pytest.raises(CompanionContractError):
        parse_companion_snapshot(payload)


def test_stale_and_future_values_do_not_become_current() -> None:
    payload = _snapshot()
    payload["fields"]["socPercent"]["quality"] = "stale"
    assert parse_companion_snapshot(payload).usable_value("socPercent") is None
    payload["fields"]["socPercent"].update(
        value=None, quality="future_clock", reason=None
    )
    assert parse_companion_snapshot(payload).usable_value("socPercent") is None


def test_conflicting_raw_range_remains_unavailable() -> None:
    payload = _snapshot()
    payload["fields"]["rangeKm"] = _field(
        None, "km", None, quality="unavailable", reason="conflicting_same_time"
    )
    assert parse_companion_snapshot(payload).usable_value("rangeKm") is None


@pytest.mark.parametrize(
    ("path", "value"),
    [
        (("schemaVersion",), 2),
        (("identity", "ownership"), "claimed"),
        (("identity", "vin"), "private-value"),
        (("sourceGeneration",), True),
        (("capabilities", "controls"), True),
        (("fields", "socPercent", "value"), True),
        (("fields", "maximumSocPercent", "value"), 70),
        (("fields", "vehicleState", "value"), "invented"),
        (("fields", "rangeKm", "value"), 269),
        (("fields", "socPercent", "sourceTimestamp"), "not-a-date"),
        (("fields", "socPercent", "sourceTimestamp"), "2026-10-20T19:01:00.000Z"),
        (("fields", "socPercent", "sourceEndpoint"), "trip_status"),
        (("fields", "socPercent", "reason"), "unit_unverified"),
    ],
)
def test_malformed_or_unverified_data_is_rejected_without_echo(
    path: tuple[str, ...], value: object
) -> None:
    payload = deepcopy(_snapshot())
    target = payload
    for key in path[:-1]:
        target = target[key]
    target[path[-1]] = value
    with pytest.raises(CompanionContractError) as caught:
        parse_companion_snapshot(payload)
    assert "private-value" not in str(caught.value)
    assert "not-a-date" not in str(caught.value)


def test_synthetic_proof_requires_explicit_parser_allowance() -> None:
    payload = _snapshot()
    payload["synthetic"] = True
    with pytest.raises(CompanionContractError):
        parse_companion_snapshot(payload)
    assert parse_companion_snapshot(payload, allow_synthetic=True).vin == "A" * 17


def test_missing_or_extra_field_fails_closed() -> None:
    payload = _snapshot()
    del payload["fields"]["socPercent"]
    with pytest.raises(CompanionContractError):
        parse_companion_snapshot(payload)
    payload = _snapshot()
    payload["fields"]["location"] = _field("private-value", None, None)
    with pytest.raises(CompanionContractError):
        parse_companion_snapshot(payload)


@pytest.mark.parametrize(
    ("status", "code", "expected"),
    [
        (401, "unauthorized", "consumer_reauthentication_required"),
        (429, "rate_limited", "retry_later"),
        (503, "source_reauthorization_required", "upstream_reauthorization_required"),
        (503, "source_disconnected", "source_disconnected"),
        (503, "unavailable", "retry_later"),
    ],
)
def test_error_classification_preserves_auth_boundary(
    status: int, code: str, expected: str
) -> None:
    assert classify_companion_error(status, {"error": code}) == expected


def test_unknown_error_envelope_fails_closed_without_leaking_body() -> None:
    with pytest.raises(CompanionContractError) as caught:
        classify_companion_error(503, {"error": "private-value"})
    assert "private-value" not in str(caught.value)
