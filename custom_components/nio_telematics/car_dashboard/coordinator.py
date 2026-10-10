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
from .ledger import Ledger, number

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
        self.source_status = "waiting_for_fresh_sample"
        self.pending_soc = None

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
            if history:
                self.ledger.import_home(history.attributes.get("sessions", []))
            odo = self.hass.states.get(self.settings["odometer"])
            rng = self.hass.states.get(self.settings["range"])
            soc = (
                self.hass.states.get(self.settings["soc"])
                if self.settings["soc"]
                else None
            )
            connected = self.hass.states.get(self.settings["home_connected"])
            self.ledger.tick(now)
            if self.settings["soc"]:
                # A native event may arrive before the corresponding odometer
                # snapshot. Hold it briefly, but never pair with distant data.
                soc_value = number(soc.state) if soc else None
                if (
                    soc
                    and soc_value is not None
                    and 0 <= soc_value <= 100
                    and not soc.attributes.get("data_retained", False)
                ):
                    stamp = _source_time(soc, "last_valid_sample")
                    if stamp is not None and 0 <= now - stamp <= 900:
                        last = self.ledger.data["last"]
                        if (
                            last is None
                            or last.get("energy_source") != "native_soc"
                            or last.get("soc") != soc_value
                        ):
                            self.pending_soc = (stamp, soc_value)
                if self.pending_soc and odo:
                    t, value = self.pending_soc
                    odo_t = _source_time(odo, "source_sample")
                    if now - t > 900:
                        self.pending_soc = None
                    elif (
                        odo_t is not None
                        and abs(odo_t - t) <= 180
                        and number(odo.state) is not None
                    ):
                        km = number(rng.state) if rng else None
                        if self.ledger.ingest(
                            t,
                            odo.state,
                            km,
                            bool(connected and connected.state == "on"),
                            soc_pct=value,
                        ):
                            self.source_status = "fresh_native_soc"
                        self.pending_soc = None
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
                            bool(connected and connected.state == "on"),
                        )
                        self.source_status = "fresh"
                    else:
                        self.source_status = "waiting_for_fresh_sample"
            if self.ledger.data["revision"] != before:
                await self.store.async_save(deepcopy(self.ledger.data))
            self.async_set_updated_data(
                {"revision": self.ledger.data["revision"], "status": self.source_status}
            )

    def snapshot(self):
        result = self.ledger.snapshot(
            dt_util.utcnow().timestamp(), self.hass.config.time_zone
        )
        result["source_status"] = self.source_status
        result["source_config"] = dict(self.settings)
        return result

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
    return stamp.timestamp() if stamp is not None else None
