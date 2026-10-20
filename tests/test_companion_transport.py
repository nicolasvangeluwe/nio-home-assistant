"""The optional Companion transport is isolated from live NIO setup."""

import json

import pytest

from custom_components.nio_telematics.companion_transport import (
    CompanionFetchError,
    CompanionVehicleClient,
    async_validate_companion_candidate,
)

VIN = "A" * 17
TOKEN = "ha1_" + "x" * 43
STAMP = "2026-10-20T18:59:07.321Z"
NOW = "2026-10-20T19:00:00.000Z"


def _field(value, unit, endpoint, *, reason=None, quality="valid"):
    return {
        "value": value,
        "unit": unit,
        "sourceTimestamp": STAMP if endpoint else None,
        "receivedAt": NOW if endpoint else None,
        "quality": quality,
        "reason": reason,
        "sourceEndpoint": endpoint,
    }


def _snapshot():
    return {
        "schemaVersion": 1,
        "vehicleKey": "a" * 64,
        "identity": {"vin": VIN, "ownership": "verified"},
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
            "targetSocPercent": _field(90, "%", "soc_status"),
            "maximumSocPercent": _field(90, "%", "soc_status"),
            "batteryCurrentA": _field(0.4, "A", "soc_status"),
            "vehicleState": _field("PARKED_VEHICLE", None, "vehicle_status"),
            "energyChargingState": _field("NO_CHARGING", None, "soc_status"),
            "dynamicsChargingState": _field("NOT_CHARGING", None, "vehicle_status"),
            "rangeKm": _field(
                None,
                "km",
                "soc_status",
                reason="unit_unverified",
                quality="unavailable",
            ),
            "odometerKm": _field(
                None,
                "km",
                "vehicle_status",
                reason="unit_unverified",
                quality="unavailable",
            ),
        },
    }


class _Content:
    def __init__(self, body):
        self.body = body

    async def read(self, maximum):
        return self.body[:maximum]


class _Response:
    def __init__(self, status, payload):
        self.status = status
        self.content = _Content(
            payload if isinstance(payload, bytes) else json.dumps(payload).encode()
        )

    async def __aenter__(self):
        return self

    async def __aexit__(self, *_):
        return None


class _Session:
    def __init__(self, status, payload):
        self.response = _Response(status, payload)
        self.calls = []

    def get(self, url, **kwargs):
        self.calls.append((url, kwargs))
        return self.response


def _client(status=200, payload=None):
    session = _Session(status, _snapshot() if payload is None else payload)
    return (
        CompanionVehicleClient(
            session,
            api_origin="https://companion.example",
            credential=TOKEN,
        ),
        session,
    )


@pytest.mark.asyncio
async def test_one_owner_bound_read_is_private_and_does_not_follow_redirects():
    client, session = _client()
    snapshot = await client.async_fetch(expected_vin=VIN)
    assert snapshot.usable_value("socPercent") == 48.5
    assert snapshot.usable_value("rangeKm") is None
    assert session.calls[0][0] == "https://companion.example/ha/v1/vehicle"
    assert session.calls[0][1]["allow_redirects"] is False
    assert session.calls[0][1]["headers"]["Authorization"] == f"Bearer {TOKEN}"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("status", "code", "kind"),
    [
        (401, "unauthorized", "consumer_reauthentication_required"),
        (503, "source_reauthorization_required", "upstream_reauthorization_required"),
        (503, "source_disconnected", "source_disconnected"),
        (503, "unavailable", "retry_later"),
        (429, "rate_limited", "retry_later"),
        (502, "provider private failure", "retry_later"),
        (403, "private failure", "invalid_response"),
    ],
)
async def test_status_classification_and_redaction(status, code, kind):
    client, _ = _client(status, {"error": code, "secret": "private-response"})
    with pytest.raises(CompanionFetchError) as caught:
        await client.async_fetch(expected_vin=VIN)
    assert caught.value.kind == kind
    assert "private-response" not in str(caught.value)
    assert "ha1_" not in str(caught.value)


@pytest.mark.asyncio
async def test_owner_vehicle_mismatch_never_switches():
    payload = _snapshot()
    payload["identity"]["vin"] = "B" * 17
    client, _ = _client(payload=payload)
    with pytest.raises(CompanionFetchError, match="identity_mismatch"):
        await client.async_fetch(expected_vin=VIN)


@pytest.mark.asyncio
async def test_vehicle_key_is_pinned_after_initial_owner_validation():
    client, _ = _client()
    with pytest.raises(CompanionFetchError, match="identity_mismatch"):
        await client.async_fetch(expected_vin=VIN, expected_vehicle_key="b" * 64)


@pytest.mark.asyncio
async def test_invalid_payload_does_not_expose_private_response_in_exception():
    client, _ = _client(payload=b'{"private":"do-not-log"}')
    with pytest.raises(CompanionFetchError) as caught:
        await client.async_fetch(expected_vin=VIN)
    assert caught.value.kind == "invalid_response"
    assert "do-not-log" not in str(caught.value)
    assert caught.value.__cause__ is None


@pytest.mark.asyncio
async def test_existing_direct_coverage_gate_rejects_proof_contract():
    client, _ = _client()
    with pytest.raises(CompanionFetchError, match="insufficient_coverage"):
        await async_validate_companion_candidate(client, expected_vin=VIN)
    candidate = await async_validate_companion_candidate(
        client, expected_vin=VIN, required_fields=("socPercent",)
    )
    assert candidate.snapshot.vin == VIN


@pytest.mark.parametrize(
    "origin",
    [
        "http://companion.example",
        "https://user:pass@companion.example",
        "https://companion.example/ha/v1/vehicle?vin=private",
    ],
)
def test_rejects_non_https_or_embedded_identity(origin):
    with pytest.raises(ValueError, match="Invalid Companion API origin"):
        CompanionVehicleClient(
            _Session(200, _snapshot()), api_origin=origin, credential=TOKEN
        )


@pytest.mark.parametrize(
    "credential", ["ha1_short", "ha1_" + "x" * 42 + "\n", "nio_token"]
)
def test_rejects_non_consumer_or_malformed_credential(credential):
    with pytest.raises(ValueError, match="Invalid Companion consumer credential"):
        CompanionVehicleClient(
            _Session(200, _snapshot()),
            api_origin="https://companion.example",
            credential=credential,
        )


@pytest.mark.asyncio
async def test_rejects_oversized_or_non_json_response():
    for payload in (b"x" * 65537, b"<html>private response</html>"):
        client, _ = _client(payload=payload)
        with pytest.raises(CompanionFetchError, match="invalid_response"):
            await client.async_fetch(expected_vin=VIN)
