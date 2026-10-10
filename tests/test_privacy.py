"""Diagnostic attributes must remain bounded and free of private telemetry."""

from custom_components.nio_telematics.privacy import safe_diagnostic_attributes


def test_redacts_identifiers_locations_and_urls() -> None:
    payload = {
        "vin": "LJNABC12345678901",
        "vehicle_uuid": "secret-vehicle",
        "btry_pak_sn": "secret-pack",
        "lat": 52.5,
        "longitude": 13.4,
        "download_url": "https://example.invalid/?signature=secret",
        "records": [{"speed": 42}],
    }
    result = safe_diagnostic_attributes(payload)
    for key in (
        "vin",
        "vehicle_uuid",
        "btry_pak_sn",
        "lat",
        "longitude",
        "download_url",
    ):
        assert result[key] == "**REDACTED**"
    assert result["records"] == [{"speed": 42}]


def test_large_lists_and_attributes_are_bounded() -> None:
    assert len(safe_diagnostic_attributes({"values": list(range(100))})["values"]) == 50
    assert safe_diagnostic_attributes({"value": "x" * 20_000}) == {
        "payload_truncated": True
    }
