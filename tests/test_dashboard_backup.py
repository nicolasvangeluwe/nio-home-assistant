"""Dashboard exports are portable only to the same car and exclude OAuth."""

from copy import deepcopy

import pytest

from custom_components.nio_telematics.dashboard_backup import (
    history_summary,
    make_backup,
    parse_backup,
)

VIN = "HJNNBDLH3SB701418"


def history():
    return {
        "trips": [{"id": "trip-1", "start": 100, "end": 200}],
        "charges": {"home-1": {"id": "home-1", "start": 300, "end": 400}},
        "samples": [{"t": 100, "odometer": 1000}],
        "counters": [],
        "parked_losses": [],
        "source_transitions": [],
        "native_replays": {},
        "last": None,
        "active": None,
        "opening": None,
        "preferences": {},
        "revision": 4,
    }


def test_round_trip_includes_history_and_settings_but_not_vin_or_tokens():
    backup = make_backup(VIN, {"model": "ET5 Touring", "language": "nl"}, history())
    assert VIN not in str(backup)
    assert "access_token" not in str(backup)
    preferences, restored = parse_backup(backup, VIN)
    assert preferences["language"] == "nl"
    assert restored == history()
    assert history_summary(restored) == {
        "trips": 1,
        "charges": 1,
        "samples": 1,
        "revision": 4,
    }
    restored["trips"].clear()
    assert backup["history"]["trips"]


def test_wrong_vehicle_and_newer_schema_are_rejected():
    backup = make_backup(VIN, {}, history())
    with pytest.raises(ValueError, match="different vehicle"):
        parse_backup(backup, "OTHER123456789012")
    newer = deepcopy(backup)
    newer["version"] = 2
    with pytest.raises(ValueError, match="version"):
        parse_backup(newer, VIN)


def test_malformed_or_sensitive_history_is_rejected():
    invalid = history()
    invalid["samples"] = "not samples"
    with pytest.raises(ValueError, match="samples"):
        make_backup(VIN, {}, invalid)
    sensitive = history()
    sensitive["charges"]["home-1"]["refresh_token"] = "secret"
    with pytest.raises(ValueError, match="credential"):
        make_backup(VIN, {}, sensitive)


def test_preferences_only_backup_does_not_request_history_replacement():
    backup = make_backup(VIN, {"language": "en"}, None)
    preferences, archived = parse_backup(backup, VIN)
    assert preferences == {"language": "en"}
    assert archived is None
    assert history_summary(archived)["revision"] is None


def test_currency_metadata_and_mixed_amounts_survive_backup_unchanged():
    archive = history()
    archive["preferences"] = {"currency": "EUR", "opening_price_eur_kwh": 0.3}
    archive["charges"]["home-1"].update(currency="EUR", cost_eur=2)
    archive["charges"]["home-2"] = {"currency": "DKK", "cost_eur": 14.92}
    backup = make_backup(VIN, {}, archive)
    _, restored = parse_backup(backup, VIN)
    assert restored == archive


@pytest.mark.parametrize("currency", [None, "dkk", "EUR<script>", 123])
def test_invalid_explicit_history_currency_is_rejected(currency):
    archive = history()
    archive["charges"]["home-1"]["currency"] = currency
    with pytest.raises(ValueError, match="currency"):
        make_backup(VIN, {}, archive)


def test_manual_and_ignored_gap_overlays_round_trip_without_archive_changes():
    archive = history()
    archive["gap_resolutions"] = {
        "gap-" + "a" * 24: {
            "fingerprint": "b" * 64,
            "status": "manual",
            "energy_kwh": 12,
            "cost": -0.6,
            "currency": "DKK",
        },
        "gap-" + "c" * 24: {"fingerprint": "d" * 64, "status": "ignored"},
    }
    _, restored = parse_backup(make_backup(VIN, {}, archive), VIN)
    assert restored == archive


@pytest.mark.parametrize(
    "update",
    [
        {"energy_kwh": -1},
        {"energy_kwh": True},
        {"cost": float("inf")},
        {"status": "open"},
        {"fingerprint": "stale"},
        {"currency": "dkk"},
    ],
)
def test_malformed_gap_overlay_is_rejected_before_restore(update):
    archive = history()
    archive["gap_resolutions"] = {
        "gap-" + "a" * 24: {
            "fingerprint": "b" * 64,
            "status": "manual",
            "energy_kwh": 12,
            "cost": 3.6,
            "currency": "DKK",
            **update,
        }
    }
    with pytest.raises(ValueError, match="gap"):
        make_backup(VIN, {}, archive)
