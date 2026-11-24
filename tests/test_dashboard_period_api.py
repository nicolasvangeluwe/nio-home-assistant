"""Read-only calendar websocket contract and its legacy compatibility."""

import inspect
from copy import deepcopy
from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import Mock
from zoneinfo import ZoneInfo

import pytest

from custom_components.nio_telematics import car_dashboard
from custom_components.nio_telematics.car_dashboard.ledger import Ledger


async def call(hass, connection, message):
    result = car_dashboard.websocket_get(hass, connection, message)
    if inspect.isawaitable(result):
        await result
    await hass.async_block_till_done()


@pytest.fixture
async def ledger_api(hass, monkeypatch):
    now = datetime(2026, 11, 23, 12, tzinfo=UTC)
    tz = ZoneInfo("Europe/Brussels")
    await hass.config.async_set_time_zone("Europe/Brussels")
    ledger = Ledger({"capacity_kwh": 90, "full_range_km": 450})
    for minutes, odo, remaining in [(0, 1000, 250), (10, 1010, 240), (20, 1020, 230)]:
        ledger.ingest(now.timestamp() - 3600 + minutes * 60, odo, remaining)
    recorder = SimpleNamespace(
        ledger=ledger, snapshot=lambda: ledger.snapshot(now.timestamp(), tz)
    )
    hass.data[car_dashboard.DATA_KEY] = {"recorders": {"one": recorder}}
    monkeypatch.setattr(car_dashboard.dt_util, "utcnow", lambda: now)
    return ledger, recorder


async def test_legacy_get_response_is_unchanged(hass, ledger_api):
    _, recorder = ledger_api
    expected = recorder.snapshot()
    connection = Mock()
    await call(hass, connection, {"id": 1, "entry_id": "one"})
    connection.send_result.assert_called_once_with(1, expected)
    connection.send_error.assert_not_called()


async def test_calendar_get_adds_selected_statistics_without_writing(hass, ledger_api):
    ledger, recorder = ledger_api
    before = deepcopy(ledger.data)
    legacy = recorder.snapshot()
    connection = Mock()
    await call(
        hass,
        connection,
        {"id": 2, "entry_id": "one", "period": "week", "date": "2026-11-23"},
    )
    result = connection.send_result.call_args.args[1]
    assert result["selected_period"]["start_date"] == "2026-11-23"
    assert result["selected_period"]["timezone"] == "Europe/Brussels"
    assert result["statistics"]["selected"]["distance_km"] == 20
    assert result["statistics"]["month"] == legacy["statistics"]["month"]
    assert result["trips"] == legacy["trips"]
    assert ledger.data == before


@pytest.mark.parametrize(
    "message",
    [
        {"entry_id": "missing", "period": "month"},
        {"entry_id": "missing"},
    ],
)
async def test_unknown_entry_preserves_not_configured_error(hass, ledger_api, message):
    connection = Mock()
    await call(hass, connection, {"id": 3, **message})
    assert connection.send_error.call_args.args[1] == "not_configured"
    connection.send_result.assert_not_called()


@pytest.mark.parametrize(
    "message",
    [
        {"period": "day", "date": "2026-02-30"},
        {"date": "2026-11-23"},
    ],
)
async def test_invalid_calendar_request_is_a_visible_error(hass, ledger_api, message):
    connection = Mock()
    await call(hass, connection, {"id": 4, "entry_id": "one", **message})
    assert connection.send_error.call_args.args[1] == "invalid_period"
    connection.send_result.assert_not_called()
