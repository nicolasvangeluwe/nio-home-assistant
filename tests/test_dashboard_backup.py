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
