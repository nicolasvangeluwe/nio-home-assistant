"""HA adapter: source listeners, aligned fresh samples and atomic durable storage."""

import asyncio
import logging
from copy import deepcopy
from datetime import timedelta

from homeassistant.core import callback
from homeassistant.helpers.event import (
    async_call_later,
    async_track_state_change_event,
    async_track_time_interval,
)
from homeassistant.helpers.storage import Store
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.util import dt as dt_util

from .const import DEFAULTS, DOMAIN
from .cost_adapter import CostRecorder
from .ledger import Ledger, number, provisional_home_charge

_LOGGER = logging.getLogger(__name__)


class CarLedgerCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, entry):
        super().__init__(hass, _LOGGER, name=DOMAIN)
        self.entry = entry
        self.settings = {**DEFAULTS, **entry.data}
        self.store = Store(hass, 1, f"{DOMAIN}.{entry.entry_id}", atomic_writes=True)
        self.lock = asyncio.Lock()
        self.unsub = []
        self.pending = None
        self.ledger = None
        self.cost_recorder = CostRecorder(self)
        self.source_status = "waiting_for_fresh_sample"
        self.active_home_id = None

    async def async_start(self):
        self.ledger = Ledger(self.settings, await self.store.async_load())
        before = self.ledger.data["revision"]
        self.ledger.classify_recorded_intervals()
        if self.ledger.data["revision"] != before:
            await self.store.async_save(deepcopy(self.ledger.data))
        entities = [
            self.settings[k]
            for k in ("odometer", "range", "soc", "home_connected", "home_history")
            if self.settings[k]
        ]
        self.unsub.append(
            async_track_state_change_event(self.hass, entities, self.source_changed)
        )
        self.unsub.append(
            async_track_time_interval(self.hass, self.timer, timedelta(minutes=1))
        )
        await self.sample()

    @callback
    def source_changed(self, event):
        if self.pending:
            self.pending()
        self.pending = async_call_later(self.hass, 3, self.debounced_sample)

    async def debounced_sample(self, now):
        self.pending = None
        await self.sample()

    async def timer(self, now):
        await self.sample()

    async def sample(self):
        async with self.lock:
            before = self.ledger.data["revision"]
            now = dt_util.utcnow().timestamp()
            history = self.hass.states.get(self.settings["home_history"])
            connected = self.hass.states.get(self.settings["home_connected"])
            if not _is_connected(connected):
                self.active_home_id = None
            elif history and history.attributes.get("active_session_id") not in (
                None,
                "",
            ):
                self.active_home_id = "home-" + str(
                    history.attributes["active_session_id"]
                )
            if history:
                self.ledger.import_home(
                    history.attributes.get("sessions", []),
                    active_session_id=history.attributes.get("active_session_id"),
                )
            if (
                self.active_home_id
                and not (history and history.attributes.get("active_session_id"))
                and self.active_home_id in self.ledger.data["charges"]
                and not self.ledger.data["charges"][self.active_home_id].get("ongoing")
            ):
                self.active_home_id = None
            odo = self.hass.states.get(self.settings["odometer"])
            rng = self.hass.states.get(self.settings["range"])
            soc = (
                self.hass.states.get(self.settings["soc"])
                if self.settings["soc"]
                else None
            )
            self.ledger.tick(now)
            if self.settings["soc"]:
                # Odometer reports define distance windows. A fresh unchanged
                # SoC is still evidence; never gate samples on value changes.
                # The endpoints are asynchronous, so use source timestamps,
                # never an unchanged cached odometer as proof of parking.
                soc_value = number(soc.state) if soc else None
                soc_t = _source_time(soc, "last_valid_sample") if soc else None
                odo_t = _source_time(odo, "source_sample") if odo else None
                if (
                    soc
                    and odo
                    and soc_value is not None
                    and 0 <= soc_value <= 100
                    and number(odo.state) is not None
                    and soc_t is not None
                    and odo_t is not None
                    and -30 <= now - odo_t <= 900
                    and -30 <= now - soc_t <= 900
                ):
                    if self.ledger.observe_native_sources(
                        odo_t,
                        odo.state,
                        soc_t,
                        soc_value,
                        _is_connected(connected),
                        connected.last_changed.timestamp() if connected else None,
                    ):
                        self.source_status = "fresh_native_soc"
                else:
                    self.source_status = "waiting_for_aligned_odometer"
            elif odo and rng:
                # Retained readings may appear in the header, not as new trip evidence.
                fresh = not rng.attributes.get("data_retained", False)
                timestamp = rng.attributes.get("last_valid_sample")
                stamp = (
                    dt_util.parse_datetime(timestamp)
                    if isinstance(timestamp, str)
                    else rng.last_updated
                )
                if stamp is not None:
                    t = stamp.timestamp()
                    reported = getattr(
                        odo, "last_reported", odo.last_updated
                    ).timestamp()
                    fresh = fresh and -30 <= now - t <= 900 and abs(reported - t) <= 120
                    if (
                        fresh
                        and number(odo.state) is not None
                        and number(rng.state) is not None
                    ):
                        self.ledger.ingest(
                            t,
                            odo.state,
                            rng.state,
                            _is_connected(connected),
                        )
                        self.source_status = "fresh"
                    else:
                        self.source_status = "waiting_for_fresh_sample"
            try:
                await self.cost_recorder.refresh(now)
            except Exception:  # Recorder startup/unavailability must not stop trips.
                _LOGGER.warning("Car cost recording could not refresh", exc_info=True)
            if self.ledger.data["revision"] != before:
                await self.store.async_save(deepcopy(self.ledger.data))
            self.async_set_updated_data(
                {"revision": self.ledger.data["revision"], "status": self.source_status}
            )

    def snapshot(self):
        now = dt_util.utcnow().timestamp()
        result = self.ledger.snapshot(now, self.hass.config.time_zone)
        connected = self.hass.states.get(self.settings["home_connected"])
        if self.active_home_id and _is_connected(connected):
            active = result["active_home_charge"]
            if active is None:
                # EVCC lists a session in history only after it completes. A
                # connected, identified session still needs a live card; keep
                # this provisional projection out of the durable trip ledger.
                evidence = self.ledger.data.get("cost_split_results", {}).get(
                    self.active_home_id, {}
                )
                signature = evidence.get("signature", [])
                start = number(signature[1]) if len(signature) > 1 else None
                if start is None or not 0 < start <= now:
                    start = connected.last_changed.timestamp()
                sources = self.settings.get("cost_sources") or {}

                def live_value(key):
                    state = (
                        self.hass.states.get(sources[key]) if key in sources else None
                    )
                    return number(state.state) if state else None

                active = provisional_home_charge(
                    self.active_home_id,
                    start,
                    now,
                    live_value("energy"),
                    live_value("total_cost"),
                    live_value("solar"),
                )
                result["active_home_charge"] = active
                result["charges"].insert(0, active)
        result["source_status"] = self.source_status
        result["source_config"] = dict(self.settings)
        return self.cost_recorder.enrich(result)

    async def mutate(self, action, values):
        async with self.lock:
            saved = deepcopy(self.ledger.data)
            now = dt_util.utcnow().timestamp()
            try:
                if action == "preferences":
                    self.ledger.preferences(values)
                elif action == "counter":
                    self.ledger.counter(now=now, **values)
                elif action == "recover_history":
                    self.ledger.recover_history(now=now, **values)
                elif action == "repair_native_trip":
                    self.ledger.repair_native_trip(now=now, **values)
                else:
                    if action == "add_charge" and (
                        number(values.get("end")) is None
                        or float(values["end"]) > now + 60
                    ):
                        raise ValueError("Charging end cannot be in the future")
                    getattr(self.ledger, action)(**values)
                await self.store.async_save(deepcopy(self.ledger.data))
            except Exception:
                self.ledger.data = saved
                raise
            self.async_set_updated_data(
                {"revision": self.ledger.data["revision"], "status": self.source_status}
            )
            return self.snapshot()

    async def async_stop(self):
        if self.pending:
            self.pending()
        for unsub in self.unsub:
            unsub()
        async with self.lock:
            await self.store.async_save(deepcopy(self.ledger.data))


def _source_time(state, attribute):
    raw = state.attributes.get(attribute)
    stamp = dt_util.parse_datetime(raw) if isinstance(raw, str) else None
    if stamp is not None:
        return stamp.timestamp()
    # User-selected HA sensors need not expose NIO's source timestamp.
    reported = getattr(state, "last_reported", None) or state.last_updated
    return reported.timestamp() if reported is not None else None


def _is_connected(state):
    return bool(
        state
        and str(state.state).lower()
        in {"on", "true", "1", "connected", "plugged", "plugged_in"}
    )
