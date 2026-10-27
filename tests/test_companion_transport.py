"""The optional Companion transport is isolated from live NIO setup."""

import json
from unittest.mock import AsyncMock, patch

import pytest
from aiohttp import ClientConnectionError

from custom_components.nio_telematics.companion_transport import (
    CompanionFetchError,
    CompanionVehicleClient,
    async_validate_companion_candidate,
)

VIN = "A" * 17
TOKEN = "ha1_" + "x" * 43
STAMP = "2026-10-20T18:59:07.321Z"
NOW = "2026-10-20T19:00:00.000Z"


@pytest.fixture(autouse=True)
def freeze_contract_clock(freezer):
    freezer.move_to(NOW)
    with patch(
        "custom_components.nio_telematics.companion_transport.asyncio.sleep",
        new_callable=AsyncMock,
    ):
        yield


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
        self.offset = 0

    async def read(self, maximum):
        chunk = self.body[self.offset : self.offset + maximum]
        self.offset += len(chunk)
        return chunk


class _Response:
    def __init__(self, status, payload):
        self.status = status
        self.headers = {}
        self.content = _Content(
            payload if isinstance(payload, bytes) else json.dumps(payload).encode()
        )

    async def __aenter__(self):
        self.content.offset = 0
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


@pytest.mark.asyncio
async def test_switch_preflight_accepts_only_verified_full_coverage():
    payload = _snapshot()
    payload["fields"]["rangeKm"] = _field(269, "km", "soc_status")
    payload["fields"]["odometerKm"] = _field(6428, "km", "vehicle_status")
    client, _ = _client(payload=payload)
    candidate = await async_validate_companion_candidate(client, expected_vin=VIN)
    assert candidate.snapshot.usable_value("socPercent") == 48.5
    assert candidate.snapshot.usable_value("rangeKm") == 269.0
    assert candidate.snapshot.usable_value("odometerKm") == 6428.0


@pytest.mark.asyncio
async def test_verified_odometer_alone_does_not_pass_existing_car_switch_gate():
    payload = _snapshot()
    payload["fields"]["odometerKm"] = _field(6428, "km", "vehicle_status")
    client, _ = _client(payload=payload)
    with pytest.raises(CompanionFetchError, match="insufficient_coverage"):
        await async_validate_companion_candidate(client, expected_vin=VIN)


@pytest.mark.asyncio
async def test_switch_rejects_old_fields_even_when_server_calls_them_valid(freezer):
    payload = _snapshot()
    payload["fields"]["rangeKm"] = _field(269, "km", "soc_status")
    payload["fields"]["odometerKm"] = _field(6428, "km", "vehicle_status")
    freezer.move_to("2026-10-20T19:20:00Z")
    client, _ = _client(payload=payload)
    with pytest.raises(CompanionFetchError, match="insufficient_coverage"):
        await async_validate_companion_candidate(client, expected_vin=VIN)


@pytest.mark.asyncio
async def test_persistent_credential_has_no_local_expiration():
    from custom_components.nio_telematics.companion_transport import (
        is_persistent_credential,
    )

    credential = "hap1_" + "x" * 43
    assert is_persistent_credential(credential)
    assert not is_persistent_credential(TOKEN)
    session = _Session(200, _snapshot())
    client = CompanionVehicleClient(
        session, api_origin="https://companion.example", credential=credential
    )
    await client.async_fetch(expected_vin=VIN)
    assert session.calls[0][1]["headers"]["Authorization"] == f"Bearer {credential}"


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


@pytest.mark.asyncio
async def test_response_can_arrive_in_multiple_small_network_chunks():
    class Chunked(_Content):
        async def read(self, maximum):
            return await super().read(min(maximum, 13))

    client, session = _client()
    session.response.content = Chunked(json.dumps(_snapshot()).encode())
    parsed = await client.async_fetch(expected_vin=VIN)
    assert parsed.usable_value("socPercent") == 48.5


@pytest.mark.asyncio
@pytest.mark.parametrize("retry_after,expected", [(None, 1), ("1", 1), ("2", 2)])
async def test_owner_admission_retries_one_cache_get(retry_after, expected):
    client, session = _client(429, {"error": "rate_limited"})
    denied = session.response
    if retry_after:
        denied.headers["Retry-After"] = retry_after
    success = _Response(200, _snapshot())
    with patch(
        "custom_components.nio_telematics.companion_transport.asyncio.sleep",
        new_callable=AsyncMock,
    ) as sleep:
        sleep.side_effect = lambda _: setattr(session, "response", success)
        result = await client.async_fetch(expected_vin=VIN)
    assert result.usable_value("socPercent") == 48.5
    sleep.assert_awaited_once_with(expected)
    assert len(session.calls) == 2


@pytest.mark.asyncio
async def test_long_retry_delay_is_propagated_without_early_request():
    client, session = _client(429, {"error": "rate_limited"})
    session.response.headers["Retry-After"] = "120"
    with pytest.raises(CompanionFetchError) as caught:
        await client.async_fetch(expected_vin=VIN)
    assert caught.value.retry_after == 120
    assert len(session.calls) == 1


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "error,reason",
    [(TimeoutError(), "timeout"), (ClientConnectionError("private-host"), "network")],
)
async def test_network_diagnostics_are_safe_and_distinct(error, reason):
    client, session = _client()
    with patch.object(session, "get", side_effect=error):
        with pytest.raises(CompanionFetchError) as caught:
            await client.async_fetch(expected_vin=VIN)
    assert caught.value.kind == "retry_later"
    assert caught.value.reason == reason
    assert caught.value.status is None
    assert caught.value.duration_ms is not None
    assert "private-host" not in str(caught.value)


@pytest.mark.asyncio
async def test_http_failure_diagnostics_and_admission_retry_boundary():
    client, session = _client(503, {"error": "unavailable"})
    session.response.headers["Retry-After"] = "2"
    with pytest.raises(CompanionFetchError) as caught:
        await client.async_fetch(expected_vin=VIN)
    assert caught.value.kind == "retry_later"
    assert caught.value.status == 503
    assert caught.value.reason == "service_unavailable"
    assert caught.value.retry_after == 2
    assert len(session.calls) == 1  # Only 429 admission gets an immediate retry.
    session.response.headers["Retry-After"] = "Tue, 20 Oct 2026 19:02:00 GMT"
    with pytest.raises(CompanionFetchError) as caught:
        await client.async_fetch(expected_vin=VIN)
    assert caught.value.retry_after == 120
    client, _ = _client(502, b"<private server error>")
    with pytest.raises(CompanionFetchError) as caught:
        await client.async_fetch(expected_vin=VIN)
    assert caught.value.kind == "retry_later"
    assert caught.value.reason == "invalid_http_body"
    assert caught.value.status == 502
    assert "private" not in str(caught.value)
