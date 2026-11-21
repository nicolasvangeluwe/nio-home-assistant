"""Bounded adaptive polling driven by independent Home Assistant states."""

from __future__ import annotations

import asyncio
import math
import time
from datetime import UTC, datetime, timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import CALLBACK_TYPE, Event, HomeAssistant, callback
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.event import (
    async_call_later,
    async_track_point_in_time,
    async_track_state_change_event,
)
from homeassistant.util import dt as dt_util

from .const import (
    CONF_CONNECTION_METHOD,
    CONNECTION_COMPANION,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
)

POLLING_OPTIONS_KEY = "polling"
_MIN_INTERVALS = {"direct": 15, CONNECTION_COMPANION: 30}


def polling_settings_for_entry(entry: ConfigEntry) -> dict[str, Any]:
    """Return complete polling settings, retaining compatibility with old entries."""
    method = entry.data.get(CONF_CONNECTION_METHOD, "direct")
    floor = _MIN_INTERVALS.get(method, 15)
    current = int(DEFAULT_SCAN_INTERVAL.total_seconds()) if floor == 15 else floor
    raw = entry.options.get(POLLING_OPTIONS_KEY, {})
    raw = raw if isinstance(raw, dict) else {}
    interval = _bounded_int(raw.get("interval_seconds"), current, floor, 120)
    idle = _bounded_int(raw.get("idle_interval_seconds"), 120, interval, 240)
    return {
        "interval_seconds": interval,
        "idle_interval_seconds": idle,
        "adaptive": raw.get("adaptive") is True,
        "connected_entity": _entity_id(raw.get("connected_entity")),
        "charging_entity": _entity_id(raw.get("charging_entity")),
        "power_entity": _entity_id(raw.get("power_entity")),
    }


def validate_polling_settings(
    hass: HomeAssistant, entry: ConfigEntry, mapping: dict[str, Any]
) -> dict[str, Any]:
    """Validate polling values and require independent inputs when enabled."""
    method = entry.data.get(CONF_CONNECTION_METHOD, "direct")
    floor = _MIN_INTERVALS.get(method, 15)
    interval = _integral_number(mapping.get("interval_seconds"))
    idle = _integral_number(mapping.get("idle_interval_seconds"))
    if (
        interval is None
        or not floor <= interval <= 120
        or idle is None
        or not interval <= idle <= 240
        or not isinstance(mapping.get("adaptive", False), bool)
    ):
        raise ValueError("invalid_polling_interval")

    result = {
        "interval_seconds": interval,
        "idle_interval_seconds": idle,
        "adaptive": mapping.get("adaptive", False),
        "connected_entity": _entity_id(mapping.get("connected_entity")),
        "charging_entity": _entity_id(mapping.get("charging_entity")),
        "power_entity": _entity_id(mapping.get("power_entity")),
    }
    if any(
        mapping.get(key) is not None and result[key] != mapping.get(key)
        for key in ("connected_entity", "charging_entity", "power_entity")
    ):
        raise ValueError("invalid_polling_sources")
    if result["adaptive"]:
        registry = er.async_get(hass)
        selected = [
            result[key]
            for key in ("connected_entity", "charging_entity", "power_entity")
            if result[key]
        ]
        if (
            not result["connected_entity"]
            or not result["charging_entity"]
            and not result["power_entity"]
            or any(hass.states.get(entity_id) is None for entity_id in selected)
            or result["power_entity"]
            and str(
                hass.states.get(result["power_entity"]).attributes.get(
                    "unit_of_measurement", ""
                )
            )
            .strip()
            .lower()
            not in {"w", "kw"}
            or any(
                entity_id.partition(".")[0]
                not in (
                    {"binary_sensor", "sensor"} if key != "power_entity" else {"sensor"}
                )
                for key in ("connected_entity", "charging_entity", "power_entity")
                if (entity_id := result[key])
            )
            or any(
                (entity := registry.async_get(entity_id)) is not None
                and entity.platform == DOMAIN
                for entity_id in selected
            )
        ):
            raise ValueError("invalid_polling_sources")
    return result


class AdaptivePollingController:
    """Configure the HA refresh interval and independent-source wakeups."""

    def __init__(self, hass: HomeAssistant, coordinator, entry: ConfigEntry) -> None:
        self.coordinator = coordinator
        self.hass = hass
        self.entry = entry
        self.settings = polling_settings_for_entry(entry)
        self.mode = "normal"
        self.last_reason = "adaptive_disabled"
        self._unsubscribe: CALLBACK_TYPE | None = None
        self._debounce: CALLBACK_TYPE | None = None
        self._wake_deferred: CALLBACK_TYPE | None = None
        self._wake_task: asyncio.Task[None] | None = None
        self._last_wake: float | None = None
        self._read_reason = "ok"
        self._started = False
        self._apply_interval()

    @property
    def interval_seconds(self) -> int:
        if self.mode == "idle" and self.settings["adaptive"]:
            return self.settings["idle_interval_seconds"]
        return self.settings["interval_seconds"]

    async def async_start(self) -> None:
        """Set the baseline interval and subscribe to selected HA sources."""
        if self._started:
            return
        self._started = True
        self.entry.async_on_unload(self.stop)
        self.refresh_mode()
        self._subscribe()

    async def async_update_options(self) -> None:
        """Apply saved options without reloading telemetry or credentials."""
        old_interval = self.interval_seconds
        self.settings = polling_settings_for_entry(self.entry)
        self.refresh_mode()
        self._subscribe()
        if self._started and self.interval_seconds < old_interval:
            self._request_refresh_if_allowed()

    async def async_stop(self) -> None:
        """Cancel timers and remove event subscriptions on unload."""
        self.stop()

    @callback
    def stop(self) -> None:
        """Synchronously unregister all controller callbacks on entry unload."""
        self._started = False
        if self._debounce:
            self._debounce()
            self._debounce = None
        if self._wake_deferred:
            self._wake_deferred()
            self._wake_deferred = None
        if self._wake_task is not None and not self._wake_task.done():
            self._wake_task.cancel()
        self._wake_task = None
        if self._unsubscribe:
            self._unsubscribe()
            self._unsubscribe = None

    def diagnostic_status(self) -> dict[str, Any]:
        """Expose bounded polling state without source state values or credentials."""
        method = self.entry.data.get(CONF_CONNECTION_METHOD, "direct")
        selected_interval = self.interval_seconds
        effective_interval = getattr(self.coordinator, "update_interval", None)
        if not isinstance(effective_interval, timedelta):
            effective_interval = timedelta(seconds=selected_interval)
        retry_until = getattr(self.coordinator, "_retry_after_until", None)
        retry_remaining = (
            max(0.0, (retry_until - datetime.now(UTC)).total_seconds())
            if isinstance(retry_until, datetime)
            else None
        )
        return {
            "mode": self.mode,
            "selected_interval_seconds": selected_interval,
            "current_interval_seconds": int(effective_interval.total_seconds()),
            "retry_after_remaining_seconds": retry_remaining,
            "retry_after_reason": getattr(
                self.coordinator, "_retry_after_reason", None
            ),
            "configured_sources": {
                key: self.settings[key]
                for key in ("connected_entity", "charging_entity", "power_entity")
                if self.settings[key]
            },
            "last_reason": self.last_reason,
            "source_report_ages_seconds": self._source_ages(),
            "transport": "companion_cache_only"
            if method == CONNECTION_COMPANION
            else "nio_api_requests",
            "refresh_count": getattr(self.coordinator, "_polling_refresh_count", 0),
        }

    def _source_ids(self) -> list[str]:
        if not self.settings["adaptive"]:
            return []
        return [
            self.settings[key]
            for key in ("connected_entity", "charging_entity", "power_entity")
            if self.settings[key]
        ]

    def _source_ages(self) -> dict[str, float | None]:
        now = datetime.now(UTC)
        ages: dict[str, float | None] = {}
        for key in ("connected_entity", "charging_entity", "power_entity"):
            entity_id = self.settings[key]
            if not entity_id:
                continue
            state = self.hass.states.get(entity_id)
            reported = getattr(state, "last_reported", None) if state else None
            if reported is not None and reported.tzinfo is None:
                reported = reported.replace(tzinfo=UTC)
            ages[key] = (
                max(0.0, (now - reported.astimezone(UTC)).total_seconds())
                if reported
                else None
            )
        return ages

    def _subscribe(self) -> None:
        if self._unsubscribe:
            self._unsubscribe()
            self._unsubscribe = None
        entities = self._source_ids()
        if entities:
            self._unsubscribe = async_track_state_change_event(
                self.hass, entities, self._source_changed
            )

    @callback
    def _source_changed(self, _event: Event) -> None:
        if not self._started or getattr(self.entry, "pref_disable_polling", False):
            return
        if self._debounce:
            return
        self._debounce = async_track_point_in_time(
            self.hass,
            self._debounced_wake,
            dt_util.utcnow() + timedelta(seconds=2),
        )

    @callback
    def _debounced_wake(self, _now: datetime) -> None:
        self._debounce = None
        previous_mode = self.mode
        previous_interval = self.interval_seconds
        self.refresh_mode()
        if not self._started:
            return
        if (
            self.interval_seconds < previous_interval
            or self.mode == "normal"
            and (previous_mode != "normal" or self.last_reason == "unplugged")
        ):
            self._request_refresh_if_allowed()

    def _request_refresh_if_allowed(self) -> None:
        """Wake promptly, while leaving auth failures and server pacing intact."""
        if (
            not self._started
            or getattr(self.entry, "pref_disable_polling", False)
            or getattr(self.coordinator, "_polling_auth_failed", False) is True
        ):
            return
        if self._wake_task is not None and not self._wake_task.done():
            return
        now_monotonic = time.monotonic()
        eligible_at = now_monotonic
        transport_floor = (
            30
            if self.entry.data.get(CONF_CONNECTION_METHOD) == CONNECTION_COMPANION
            else 15
        )
        if self._last_wake is not None:
            eligible_at = max(eligible_at, self._last_wake + transport_floor)
        last_attempt = getattr(
            self.coordinator, "_polling_last_attempt_monotonic", None
        )
        if isinstance(last_attempt, (int, float)):
            eligible_at = max(eligible_at, last_attempt + transport_floor)
        pacer = getattr(getattr(self.coordinator, "_client", None), "_pacer", None)
        if pacer is not None:
            pacer_deadline = getattr(pacer, "_next_at", 0)
            if isinstance(pacer_deadline, (int, float)):
                eligible_at = max(eligible_at, pacer_deadline)
        retry_until = getattr(self.coordinator, "_retry_after_until", None)
        if isinstance(retry_until, datetime):
            if retry_until.tzinfo is None:
                retry_until = retry_until.replace(tzinfo=UTC)
            eligible_at = max(
                eligible_at,
                now_monotonic
                + max(
                    0.0,
                    (retry_until.astimezone(UTC) - datetime.now(UTC)).total_seconds(),
                ),
            )
        if eligible_at > now_monotonic:
            if self._wake_deferred is None:
                self._wake_deferred = async_call_later(
                    self.hass,
                    eligible_at - now_monotonic,
                    self._deferred_wake,
                )
            return
        self._last_wake = now_monotonic
        self._wake_task = self.hass.async_create_task(
            self.coordinator.async_request_refresh()
        )

    @callback
    def _deferred_wake(self, _now: datetime) -> None:
        self._wake_deferred = None
        if self._started:
            self._request_refresh_if_allowed()

    def refresh_mode(self) -> None:
        """Re-evaluate inputs and set the interval used by HA's next refresh."""
        self._refresh_mode()
        self._apply_interval()

    def _apply_interval(self) -> None:
        seconds = self.interval_seconds
        pacer = getattr(getattr(self.coordinator, "_client", None), "_pacer", None)
        pacer_deadline = getattr(pacer, "_next_at", None)
        if isinstance(pacer_deadline, (int, float)):
            seconds = max(seconds, math.ceil(pacer_deadline - time.monotonic()))
        retry_until = getattr(self.coordinator, "_retry_after_until", None)
        if isinstance(retry_until, datetime):
            seconds = max(
                seconds, math.ceil((retry_until - datetime.now(UTC)).total_seconds())
            )
        self.coordinator.update_interval = timedelta(seconds=max(1, seconds))

    def _refresh_mode(self) -> None:
        if getattr(self.coordinator, "_polling_transport_recovering", False) is True:
            self.mode, self.last_reason = "normal", "transport_recovery"
            return
        if not self.settings["adaptive"]:
            self.mode = "normal"
            self.last_reason = "adaptive_disabled"
            return
        connected = self._read(self.settings["connected_entity"], "connected")
        if connected is None:
            self.mode, self.last_reason = "normal", f"connected_{self._read_reason}"
            return
        if connected is not True:
            self.mode, self.last_reason = "normal", "unplugged"
            return
        charging = (
            self._read(self.settings["charging_entity"], "charging")
            if self.settings["charging_entity"]
            else None
        )
        charging_reason = self._read_reason
        power = (
            self._read(self.settings["power_entity"], "power")
            if self.settings["power_entity"]
            else None
        )
        power_reason = self._read_reason
        if charging is True or power == "active":
            self.mode, self.last_reason = "normal", "charging"
        elif (
            charging is False and (not self.settings["power_entity"] or power == "idle")
        ) or (
            power == "idle"
            and (not self.settings["charging_entity"] or charging is False)
        ):
            self.mode, self.last_reason = "idle", "connected_idle"
        else:
            issues = []
            if charging is None and self.settings["charging_entity"]:
                issues.append(f"charging_{charging_reason}")
            if power is None and self.settings["power_entity"]:
                issues.append(f"power_{power_reason}")
            self.mode, self.last_reason = (
                "normal",
                "configured_signal_" + "_".join(issues),
            )

    def _read(self, entity_id: str, kind: str) -> bool | str | None:
        state = self.hass.states.get(entity_id)
        if state is None or state.state in {"unknown", "unavailable"}:
            self._read_reason = "unavailable"
            return None
        attributes = state.attributes
        quality = str(attributes.get("source_quality", "")).lower()
        if (
            getattr(state, "restored", False) is True
            or attributes.get("restored") is True
            or attributes.get("assumed_state") is True
            or attributes.get("fresh") is False
            or quality in {"stale", "invalid", "unavailable"}
        ):
            self._read_reason = "source_marked_stale_or_assumed"
            return None
        value = state.state.strip().lower()
        if kind == "connected":
            self._read_reason = "ok"
            if value in {"on", "connected", "plugged", "plugged_in", "true", "yes"}:
                return True
            if value in {"off", "disconnected", "unplugged", "false", "no"}:
                return False
            self._read_reason = "ambiguous"
            return None
        if kind == "charging":
            if value in {"on", "charging", "active", "true", "yes"}:
                self._read_reason = "ok"
                return True
            if value in {
                "off",
                "idle",
                "not_charging",
                "no_charging",
                "false",
                "no",
                "complete",
                "completed",
            }:
                self._read_reason = "ok"
                return False
            self._read_reason = "ambiguous"
            return None
        unit = str(state.attributes.get("unit_of_measurement", "")).strip().lower()
        multiplier = {"w": 1.0, "kw": 1000.0}.get(unit)
        if multiplier is None:
            self._read_reason = "invalid_unit"
            return None
        try:
            number = float(value)
        except (TypeError, ValueError):
            self._read_reason = "invalid_power"
            return None
        if not math.isfinite(number) or number < 0:
            self._read_reason = "invalid_power"
            return None
        self._read_reason = "ok"
        return "active" if number * multiplier > 0 else "idle"


def _bounded_int(value: Any, default: int, minimum: int, maximum: int) -> int:
    value = _integral_number(value)
    if value is None:
        return default
    return min(max(value, minimum), maximum)


def _integral_number(value: Any) -> int | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    if not math.isfinite(value) or int(value) != value:
        return None
    return int(value)


def _entity_id(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""
