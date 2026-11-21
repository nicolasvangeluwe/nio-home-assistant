"""Adaptive polling follows independent HA charger state conservatively."""

import asyncio
from datetime import UTC, datetime, timedelta
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from homeassistant.helpers import entity_registry as er
from homeassistant.util import dt as dt_util
from pytest_homeassistant_custom_component.common import (
    MockConfigEntry,
    async_fire_time_changed,
)

from custom_components.nio_telematics.companion_coordinator import (
    CompanionDataUpdateCoordinator,
)
from custom_components.nio_telematics.const import CONF_VIN, DOMAIN
from custom_components.nio_telematics.coordinator import NioDataUpdateCoordinator
from custom_components.nio_telematics.polling import (
    POLLING_OPTIONS_KEY,
    AdaptivePollingController,
    polling_settings_for_entry,
    validate_polling_settings,
)


def _entry(options=None, method="direct"):
    return MockConfigEntry(
        domain=DOMAIN,
        title="NIO",
        data={"connection_method": method},
        options=options or {},
    )


def _options(**overrides):
    return {
        "interval_seconds": 15,
        "idle_interval_seconds": 120,
        "adaptive": True,
        "connected_entity": "binary_sensor.charger_connected",
        "charging_entity": "binary_sensor.charger_charging",
        "power_entity": "",
        **overrides,
    }


def _sources(hass, *, connected="on", charging="off", attrs=None):
    hass.states.async_set("binary_sensor.charger_connected", connected)
    hass.states.async_set("binary_sensor.charger_charging", charging, attrs or {})


def test_legacy_defaults_keep_existing_normal_polling():
    direct = polling_settings_for_entry(_entry())
    companion = polling_settings_for_entry(_entry(method="companion"))
    assert direct == {
        "interval_seconds": 15,
        "idle_interval_seconds": 120,
        "adaptive": False,
        "connected_entity": "",
        "charging_entity": "",
        "power_entity": "",
    }
    assert companion["interval_seconds"] == 30
    assert companion["adaptive"] is False


def test_validator_accepts_integer_selector_floats_and_bounds_intervals(hass):
    entry = _entry()
    assert (
        validate_polling_settings(
            hass,
            entry,
            {
                **_options(adaptive=False),
                "interval_seconds": 30.0,
                "idle_interval_seconds": 240.0,
            },
        )["interval_seconds"]
        == 30
    )
    with pytest.raises(ValueError, match="invalid_polling_interval"):
        validate_polling_settings(
            hass,
            entry,
            {**_options(adaptive=False), "interval_seconds": 14},
        )
    with pytest.raises(ValueError, match="invalid_polling_interval"):
        validate_polling_settings(
            hass,
            entry,
            {**_options(adaptive=False), "idle_interval_seconds": float("nan")},
        )


def test_validator_requires_independent_existing_binary_inputs(hass):
    entry = _entry()
    _sources(hass)
    assert validate_polling_settings(hass, entry, _options()) == _options()
    with pytest.raises(ValueError, match="invalid_polling_sources"):
        validate_polling_settings(
            hass,
            entry,
            _options(connected_entity="sensor.missing"),
        )
    own_entity = er.async_get(hass).async_get_or_create(
        "sensor",
        DOMAIN,
        "battery_state_of_charge",
        suggested_object_id="nio_telematics_battery_state_of_charge",
    )
    hass.states.async_set(own_entity.entity_id, "50")
    with pytest.raises(ValueError, match="invalid_polling_sources"):
        validate_polling_settings(
            hass,
            entry,
            _options(charging_entity=own_entity.entity_id),
        )


def test_validator_rejects_power_sensor_without_watt_unit(hass):
    entry = _entry()
    _sources(hass)
    hass.states.async_set("sensor.charger_power", "0", {"unit_of_measurement": "A"})
    with pytest.raises(ValueError, match="invalid_polling_sources"):
        validate_polling_settings(
            hass,
            entry,
            _options(power_entity="sensor.charger_power"),
        )


async def test_stable_old_reported_states_can_select_idle_but_explicit_stale_cannot(
    hass, freezer
):
    entry = _entry({POLLING_OPTIONS_KEY: _options()})
    _sources(hass)
    coordinator = MagicMock(hass=hass, last_update_success=True)
    controller = AdaptivePollingController(hass, coordinator, entry)
    await controller.async_start()
    assert controller.mode == "idle"
    assert coordinator.update_interval == timedelta(seconds=120)

    # Push integrations may legitimately leave last_reported unchanged overnight.
    freezer.move_to(datetime.now(UTC) + timedelta(minutes=20))
    controller.refresh_mode()
    assert controller.mode == "idle"
    assert (
        controller.diagnostic_status()["source_report_ages_seconds"]["charging_entity"]
        >= 1_200
    )

    hass.states.async_set("binary_sensor.charger_charging", "off", {"fresh": False})
    controller.refresh_mode()
    assert controller.mode == "normal"
    assert "stale" in controller.last_reason
    assert coordinator.update_interval == timedelta(seconds=15)
    await controller.async_stop()


async def test_power_requires_physical_unit_and_positive_value_wins(hass):
    entry = _entry({POLLING_OPTIONS_KEY: _options(power_entity="sensor.charger_power")})
    _sources(hass, charging="off")
    hass.states.async_set("sensor.charger_power", "0", {"unit_of_measurement": "kW"})
    coordinator = MagicMock(hass=hass, last_update_success=True)
    controller = AdaptivePollingController(hass, coordinator, entry)
    await controller.async_start()
    assert controller.mode == "idle"

    hass.states.async_set("sensor.charger_power", "1.2", {"unit_of_measurement": "kW"})
    controller.refresh_mode()
    assert controller.mode == "normal"
    assert controller.last_reason == "charging"

    # A positive charge-state report overrides a simultaneous zero-power report.
    hass.states.async_set("binary_sensor.charger_charging", "on")
    hass.states.async_set("sensor.charger_power", "0", {"unit_of_measurement": "W"})
    controller.refresh_mode()
    assert controller.mode == "normal"

    hass.states.async_set("sensor.charger_power", "nan", {"unit_of_measurement": "W"})
    hass.states.async_set("binary_sensor.charger_charging", "unknown")
    controller.refresh_mode()
    assert controller.mode == "normal"
    assert (
        "invalid_power" in controller.last_reason
        or "unavailable" in controller.last_reason
    )
    await controller.async_stop()


async def test_event_burst_wakes_once_on_idle_to_charging(hass):
    entry = _entry({POLLING_OPTIONS_KEY: _options()})
    _sources(hass)
    coordinator = MagicMock(hass=hass, last_update_success=True)
    coordinator.async_request_refresh = AsyncMock()
    controller = AdaptivePollingController(hass, coordinator, entry)
    await controller.async_start()

    def immediate(_hass, callback, _point):
        callback(datetime.now(UTC))
        return lambda: None

    with patch(
        "custom_components.nio_telematics.polling.async_track_point_in_time",
        side_effect=immediate,
    ):
        hass.states.async_set("binary_sensor.charger_charging", "on")
        hass.states.async_set("binary_sensor.charger_charging", "off")
        hass.states.async_set("binary_sensor.charger_charging", "on")
        await hass.async_block_till_done()
    assert controller.mode == "normal"
    assert coordinator.async_request_refresh.await_count == 1
    await controller.async_stop()
    hass.states.async_set("binary_sensor.charger_charging", "off")
    await hass.async_block_till_done()
    assert coordinator.async_request_refresh.await_count == 1


async def test_disabled_config_entry_does_not_wake_on_source_event(hass):
    entry = _entry({POLLING_OPTIONS_KEY: _options()})
    _sources(hass)
    entry.pref_disable_polling = True
    coordinator = MagicMock(hass=hass, last_update_success=True)
    coordinator.async_request_refresh = AsyncMock()
    controller = AdaptivePollingController(hass, coordinator, entry)
    await controller.async_start()
    with patch("custom_components.nio_telematics.polling.async_call_later") as later:
        hass.states.async_set("binary_sensor.charger_charging", "on")
        await hass.async_block_till_done()
    later.assert_not_called()
    coordinator.async_request_refresh.assert_not_awaited()
    await controller.async_stop()


async def test_unload_cancels_pending_event_refresh(hass):
    entry = _entry({POLLING_OPTIONS_KEY: _options()})
    _sources(hass)
    coordinator = MagicMock(hass=hass, last_update_success=True)
    began = asyncio.Event()
    hold = asyncio.Event()

    async def pending_refresh():
        began.set()
        await hold.wait()

    coordinator.async_request_refresh = pending_refresh
    controller = AdaptivePollingController(hass, coordinator, entry)
    await controller.async_start()
    controller._request_refresh_if_allowed()
    await began.wait()
    task = controller._wake_task
    await controller.async_stop()
    await hass.async_block_till_done()
    assert task is not None and task.cancelled()


async def test_charging_wake_waits_for_direct_pacer_budget(hass):
    entry = _entry({POLLING_OPTIONS_KEY: _options()})
    _sources(hass)
    coordinator = MagicMock(hass=hass, last_update_success=True)
    coordinator.async_request_refresh = AsyncMock()
    coordinator._client = SimpleNamespace(_pacer=SimpleNamespace(_next_at=110.0))
    controller = AdaptivePollingController(hass, coordinator, entry)
    await controller.async_start()
    scheduled = []
    with (
        patch(
            "custom_components.nio_telematics.polling.time.monotonic",
            return_value=100.0,
        ),
        patch(
            "custom_components.nio_telematics.polling.async_call_later",
            side_effect=lambda _hass, delay, callback: (
                scheduled.append((delay, callback)) or (lambda: None)
            ),
        ),
    ):
        controller._request_refresh_if_allowed()
    assert scheduled[0][0] == 10.0
    coordinator.async_request_refresh.assert_not_awaited()
    with patch(
        "custom_components.nio_telematics.polling.time.monotonic", return_value=110.0
    ):
        scheduled[0][1](datetime.now(UTC))
        await hass.async_block_till_done()
    coordinator.async_request_refresh.assert_awaited_once()
    await controller.async_stop()


async def test_companion_retry_after_defers_independent_event(hass, freezer):
    entry = _entry({POLLING_OPTIONS_KEY: _options()}, method="companion")
    _sources(hass)
    coordinator = MagicMock(hass=hass, last_update_success=True)
    coordinator.async_request_refresh = AsyncMock()
    coordinator._retry_after_until = datetime.now(UTC) + timedelta(seconds=45)
    controller = AdaptivePollingController(hass, coordinator, entry)
    await controller.async_start()
    scheduled = []
    with patch(
        "custom_components.nio_telematics.polling.async_call_later",
        side_effect=lambda _hass, delay, callback: (
            scheduled.append((delay, callback)) or (lambda: None)
        ),
    ):
        controller._request_refresh_if_allowed()
    assert scheduled[0][0] >= 44
    coordinator.async_request_refresh.assert_not_awaited()

    freezer.move_to(datetime.now(UTC) + timedelta(seconds=46))
    scheduled[0][1](datetime.now(UTC))
    await hass.async_block_till_done()
    coordinator.async_request_refresh.assert_awaited_once()
    await controller.async_stop()


async def test_companion_attempts_keep_thirty_second_floor_under_overlap(hass):
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Companion NIO",
        data={
            CONF_VIN: "C" * 17,
            "connection_method": "companion",
            "companion_vehicle_key": "d" * 64,
        },
    )
    clock = [100.0]
    attempts = []

    async def fetch(**_kwargs):
        attempts.append(clock[0])
        return object()

    async def sleep(seconds):
        clock[0] += seconds

    client = SimpleNamespace(async_fetch=AsyncMock(side_effect=fetch))
    coordinator = CompanionDataUpdateCoordinator(hass, entry, client)
    coordinator.polling_controller = object()
    with (
        patch(
            "custom_components.nio_telematics.companion_coordinator.time.monotonic",
            side_effect=lambda: clock[0],
        ),
        patch(
            "custom_components.nio_telematics.companion_coordinator.asyncio.sleep",
            side_effect=sleep,
        ),
    ):
        await coordinator._async_fetch_snapshot()
        clock[0] += 1
        await coordinator._async_fetch_snapshot()
    assert attempts == [100.0, 130.0]


async def test_companion_event_wake_waits_until_thirty_seconds_from_last_attempt(
    hass,
):
    entry = _entry({POLLING_OPTIONS_KEY: _options()}, method="companion")
    _sources(hass)
    coordinator = MagicMock(hass=hass, last_update_success=True)
    coordinator._polling_last_attempt_monotonic = 100.0
    coordinator.async_request_refresh = AsyncMock()
    controller = AdaptivePollingController(hass, coordinator, entry)
    await controller.async_start()
    scheduled = []
    with (
        patch(
            "custom_components.nio_telematics.polling.time.monotonic",
            return_value=101.0,
        ),
        patch(
            "custom_components.nio_telematics.polling.async_call_later",
            side_effect=lambda _hass, delay, callback: (
                scheduled.append((delay, callback)) or (lambda: None)
            ),
        ),
    ):
        controller._request_refresh_if_allowed()
        controller._request_refresh_if_allowed()
    assert scheduled[0][0] == 29.0
    assert len(scheduled) == 1
    coordinator.async_request_refresh.assert_not_awaited()
    with patch(
        "custom_components.nio_telematics.polling.time.monotonic",
        return_value=130.0,
    ):
        scheduled[0][1](datetime.now(UTC))
        await hass.async_block_till_done()
    coordinator.async_request_refresh.assert_awaited_once()
    await controller.async_stop()


class _CountedNioClient:
    """Return advancing real-source SoC while counting actual coordinator calls."""

    def __init__(self, origin):
        self.calls = 0
        self.origin = origin

    async def async_get_change_record(self, _vin, resource):
        self.calls += 1
        if resource == "soc_status":
            return {
                "soc": 50 + (dt_util.utcnow() - self.origin).total_seconds() / 10_000,
                "sample_timestamp": int(dt_util.utcnow().timestamp() * 1000),
            }
        return {}

    async def async_get_latest_vehicle_record(self, _vin):
        self.calls += 1
        return {}

    async def async_get_odometer_report(self, _vin):
        self.calls += 1
        return {}


async def test_actual_ha_scheduler_reduces_idle_calls_and_wakes_for_soc(
    hass, freezer, record_property
):
    """Compare Direct polling over one fake 30-minute clock and charging event."""
    start = datetime(2026, 11, 21, 12, 0, tzinfo=UTC)
    freezer.move_to(start)
    _sources(hass)
    baseline_entry = MockConfigEntry(
        domain=DOMAIN,
        title="Baseline NIO",
        unique_id="A" * 17,
        data={CONF_VIN: "A" * 17, "connection_method": "direct"},
        options={POLLING_OPTIONS_KEY: {"adaptive": False}},
    )
    adaptive_entry = MockConfigEntry(
        domain=DOMAIN,
        title="Adaptive NIO",
        unique_id="B" * 17,
        data={CONF_VIN: "B" * 17, "connection_method": "direct"},
        options={POLLING_OPTIONS_KEY: _options()},
    )
    baseline_entry.add_to_hass(hass)
    adaptive_entry.add_to_hass(hass)
    baseline_client = _CountedNioClient(start)
    adaptive_client = _CountedNioClient(start)
    baseline = NioDataUpdateCoordinator(hass, baseline_entry, baseline_client)
    adaptive = NioDataUpdateCoordinator(hass, adaptive_entry, adaptive_client)
    controller = AdaptivePollingController(hass, adaptive, adaptive_entry)
    adaptive.polling_controller = controller
    await controller.async_start()
    await baseline.async_config_entry_first_refresh()
    await adaptive.async_config_entry_first_refresh()
    baseline_unsub = baseline.async_add_listener(lambda: None)
    adaptive_unsub = adaptive.async_add_listener(lambda: None)

    current = start
    for _ in range(100):
        current += timedelta(seconds=15)
        freezer.move_to(current)
        async_fire_time_changed(hass, current)
        await hass.async_block_till_done()
    idle_calls = adaptive_client.calls
    record_property("adaptive_idle_requests", idle_calls)
    record_property("baseline_requests_at_1500s", baseline_client.calls)
    assert controller.mode == "idle"
    assert (current - start).total_seconds() == 1_500

    previous_soc = adaptive.data.soc_status.soc
    hass.states.async_set("binary_sensor.charger_charging", "on")
    await hass.async_block_till_done()
    current += timedelta(seconds=3)
    freezer.move_to(current)
    async_fire_time_changed(hass, current)
    await hass.async_block_till_done()
    assert adaptive_client.calls > idle_calls
    assert adaptive.data.soc_status.soc != previous_soc
    assert controller.mode == "normal"
    after_wake = adaptive_client.calls

    for _ in range(19):
        current += timedelta(seconds=15)
        freezer.move_to(current)
        async_fire_time_changed(hass, current)
        await hass.async_block_till_done()
    current += timedelta(seconds=12)
    freezer.move_to(current)
    async_fire_time_changed(hass, current)
    await hass.async_block_till_done()
    assert (current - start).total_seconds() == 1_800
    assert adaptive_client.calls < baseline_client.calls
    assert adaptive_client.calls - after_wake >= 17
    record_property("baseline_requests_at_1800s", baseline_client.calls)
    record_property("adaptive_requests_at_1800s", adaptive_client.calls)

    baseline_unsub()
    adaptive_unsub()
    await controller.async_stop()
