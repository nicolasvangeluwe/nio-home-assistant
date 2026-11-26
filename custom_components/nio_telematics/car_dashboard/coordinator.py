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
from .currency_warnings import history_currency_warning
from .ledger import (
    Ledger,
    currency_code,
    number,
    provisional_home_charge,
    source_currency,
)

_LOGGER = logging.getLogger(__name__)


class CarLedgerCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, entry):
        super().__init__(hass, _LOGGER, name=DOMAIN)
        self.entry = entry
        self.settings = {
            **DEFAULTS,
            **entry.data,
            "currency": currency_code(hass.config.currency),
        }
        self.store = Store(hass, 1, f"{DOMAIN}.{entry.entry_id}", atomic_writes=True)
        self.lock = asyncio.Lock()
        self.unsub = []
        self.pending = None
        self.ledger = None
        self.cost_recorder = CostRecorder(self)
        self.source_status = "waiting_for_fresh_sample"
        self.active_home_id = None

    async def async_start(self):
        saved = await self.store.async_load()
        before = saved["revision"] if saved else 0
        self.ledger = Ledger(self.settings, saved)
        self.ledger.classify_recorded_intervals()
        if self.ledger.currency_migrated or self.ledger.data["revision"] != before:
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
            self.sync_currency()
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
                try:
                    history_currency = source_currency(
                        history.attributes, self.ledger.currency, monetary=False
                    )
                except ValueError:
                    _LOGGER.warning(
                        "Car charging history has invalid currency metadata"
                    )
                else:
                    self.ledger.import_home(
                        history.attributes.get("sessions", []),
                        active_session_id=history.attributes.get("active_session_id"),
                        currency=history_currency,
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
            if self.ledger.data.get("native_zero_capture") and odo:
                pending_odo_t = _source_time(odo, "source_sample")
                pending_odo = number(odo.state)
                if (
                    pending_odo_t is not None
                    and pending_odo is not None
                    and odo.attributes.get("fresh", True) is not False
                    and not odo.attributes.get("data_retained", False)
                    and -30 <= now - pending_odo_t <= 900
                ):
                    self.ledger.observe_capture_odometer(pending_odo_t, pending_odo)
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
                    and soc.attributes.get("fresh", True) is not False
                    and odo.attributes.get("fresh", True) is not False
                    and soc_t is not None
                    and odo_t is not None
                    and -30 <= now - odo_t <= 900
                    and -30 <= now - soc_t <= 900
                ):
                    provenance = soc.attributes.get("telemetry_source", "direct")
                    if provenance == "companion":
                        provenance += ":" + str(soc.attributes.get("source_generation"))
                    source_changed = provenance != self.ledger.data.get(
                        "telemetry_source", "direct"
                    )
                    # Consult the accepted native baseline BEFORE an epoch
                    # clears last; a first zero from a new generation is not
                    # evidence that its source event independently changed.
                    hold = self.capture_native_zero(
                        soc, rng, odo_t, number(odo.state), now, provenance
                    )
                    guard = self.ledger.data.get("native_zero_capture")
                    if source_changed and not hold:
                        release = (
                            {
                                key: guard[key]
                                for key in (
                                    "released",
                                    "accepted_soc",
                                    "accepted_soc_at",
                                )
                            }
                            if guard
                            else None
                        )
                        self.ledger.begin_new_epoch(self.settings)
                        guard = self.ledger.data.get("native_zero_capture")
                        if release:
                            guard.update(release, needs_advanced=False)
                        self.ledger.data["telemetry_source"] = provenance
                        self.ledger.changed()
                    pending_baseline = (
                        self.ledger.pending_native_trip()
                        if guard and self.ledger.data["last"] is None
                        else None
                    )
                    if not hold and self.ledger.observe_native_sources(
                        odo_t,
                        odo.state,
                        soc_t,
                        soc_value,
                        _is_connected(connected),
                        connected.last_changed.timestamp() if connected else None,
                        force_native_gap=bool(guard),
                    ):
                        if pending_baseline:
                            pending_baseline.update(
                                capture_pending=False,
                                start_energy=None,
                                end_energy=self.ledger.data["last"]["energy"],
                            )
                            pending_baseline["segments"][0].update(
                                capture_pending=False,
                                invalid_reason="gap",
                                start_energy=None,
                                end_energy=self.ledger.data["last"]["energy"],
                            )
                            self.ledger.data["trips"].append(pending_baseline)
                            self.ledger.changed()
                        if (
                            guard
                            and self.ledger.data["last"]["odo"]
                            >= guard["latest"]["odo"]
                        ):
                            self.ledger.data.pop("native_zero_capture", None)
                            self.ledger.changed()
                        self.source_status = "fresh_native_soc"
                    elif hold or guard:
                        self.source_status = "waiting_for_validated_energy"
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

    def capture_native_zero(self, soc, rng, odo_t, odo, now, provenance):
        """Bridge native-coordinator restarts using this ledger's accepted baseline.

        Only actual matching source metadata identifies a joint zero. This
        accounting safeguard never seeds the generic integration with ledger
        data, invents an old range, or treats a generation bump as a new event.
        """

        def evidence(state, *, soc_field=False):
            if state is None:
                return None
            attrs = state.attributes
            raw = attrs.get("last_valid_sample")
            stamp = dt_util.parse_datetime(raw) if isinstance(raw, str) else None
            source = attrs.get("telemetry_source")
            source = (
                source + ":" + str(attrs.get("source_generation"))
                if source == "companion"
                else source
            )
            if (
                stamp is None
                or source != provenance
                or (soc_field and attrs.get("source_endpoint") != "soc_status")
                or attrs.get("source_endpoint") not in (None, "soc_status")
            ):
                return None
            authoritative = (
                attrs.get("fresh", True) is not False
                and not attrs.get("data_retained", False)
                and attrs.get("source_quality", "valid") == "valid"
                and -30 <= now - stamp.timestamp() <= 900
            )
            return number(state.state), stamp.timestamp(), authoritative

        # NioRangeSensor exposes its real field clock/source/quality but has
        # no source_endpoint attribute; the selected range role supplies no
        # synthetic metadata. SoC explicitly identifies the energy feed.
        soc_read, range_read = evidence(soc, soc_field=True), evidence(rng)
        joint = (
            soc_read is not None
            and range_read is not None
            and soc_read[0] == range_read[0] == 0
            and abs(soc_read[1] - range_read[1]) <= 5
        )
        guard = self.ledger.data.get("native_zero_capture")
        last = self.ledger.data["last"]
        context = (self.ledger.data.get("pending_epoch") or {}).get(
            "native_validation_baseline"
        )
        if last is None and context:
            last = dict(context["sample"], energy_source="native_soc")
        if (
            not guard
            and joint
            and last
            and last.get("energy_source") == "native_soc"
            and (number(last.get("soc")) or 0) > 1
        ):
            self.ledger.close_trip()
            guard = {
                "source": provenance,
                "capacity_kwh": context["capacity_kwh"]
                if context and self.ledger.data["last"] is None
                else last.get("capacity_kwh", self.ledger._capacity_at(last["t"])),
                "baseline": {key: last[key] for key in ("t", "odo", "soc", "energy")},
                "latest": {"t": last["t"], "odo": last["odo"]},
                "started": None,
                "soc_at": soc_read[1],
                "range_at": range_read[1],
                "released": False,
                "accepted_soc": None,
                "accepted_soc_at": None,
                "needs_advanced": False,
            }
            self.ledger.data["native_zero_capture"] = guard
            self.ledger.changed()
        if guard is None:
            return False
        before = deepcopy(guard)
        if guard["source"] != provenance:
            guard.update(
                source=provenance,
                started=None,
                released=False,
                accepted_soc=None,
                accepted_soc_at=None,
                needs_advanced=True,
            )
        baseline, latest = guard["baseline"], guard["latest"]
        if (
            odo_t > latest["t"]
            and odo >= latest["odo"]
            and odo - baseline["odo"] <= max(0, odo_t - baseline["t"]) / 3600 * 250 + 5
        ):
            latest.update(t=odo_t, odo=odo)
        if (
            guard["released"]
            and soc_read
            and soc_read[0] == guard["accepted_soc"]
            and soc_read[1] >= guard["accepted_soc_at"]
            and soc.attributes.get("source_quality", "valid") == "valid"
        ):
            hold = False
        elif (
            soc_read
            and soc_read[0] is not None
            and soc_read[0] > 0
            and soc_read[2]
            and soc_read[1] >= guard["soc_at"]
        ):
            guard["released"] = True
            guard.update(
                accepted_soc=soc_read[0],
                accepted_soc_at=soc_read[1],
                needs_advanced=False,
            )
            hold = False
        else:
            if guard["released"]:
                guard.update(
                    released=False,
                    started=None,
                    accepted_soc=None,
                    accepted_soc_at=None,
                )
            hold = True
            if (
                joint
                and soc_read[2]
                and range_read[2]
                and min(soc_read[1], range_read[1]) > baseline["t"]
            ):
                if guard["started"] is None and (
                    not guard["needs_advanced"]
                    or (
                        soc_read[1] > guard["soc_at"]
                        and range_read[1] > guard["range_at"]
                    )
                ):
                    guard["started"] = now
                    guard["needs_advanced"] = False
                elif (
                    guard["started"] is not None
                    and now - guard["started"] >= 60
                    and soc_read[1] > guard["soc_at"]
                    and range_read[1] > guard["range_at"]
                ):
                    guard["released"] = True
                    guard.update(accepted_soc=0.0, accepted_soc_at=soc_read[1])
                    hold = False
                guard["soc_at"] = max(guard["soc_at"], soc_read[1])
                guard["range_at"] = max(guard["range_at"], range_read[1])
        if not guard["released"]:
            for key, reading in (("soc_at", soc_read), ("range_at", range_read)):
                if reading and reading[0] == 0 and reading[2]:
                    guard[key] = max(guard[key], reading[1])
        if guard != before:
            self.ledger.changed()
        return hold or odo < latest["odo"]

    def sync_currency(self):
        """Apply HA's current accounting unit without relabelling saved amounts."""
        currency = currency_code(self.hass.config.currency)
        self.ledger.currency = currency
        self.settings["currency"] = currency

    def snapshot(self):
        self.sync_currency()
        now = dt_util.utcnow().timestamp()
        result = self.ledger.snapshot(
            now, dt_util.get_time_zone(self.hass.config.time_zone)
        )
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

                total_state = self.hass.states.get(sources.get("total_cost", ""))
                try:
                    history = self.hass.states.get(self.settings["home_history"])
                    history_currency = source_currency(
                        history.attributes if history else {},
                        self.ledger.currency,
                        monetary=False,
                    )
                    live_currency = source_currency(
                        total_state.attributes if total_state else {},
                        history_currency,
                        per_kwh=False,
                    )
                    live_cost = live_value("total_cost")
                except ValueError:
                    live_currency, live_cost = self.ledger.currency, None
                active = provisional_home_charge(
                    self.active_home_id,
                    start,
                    now,
                    live_value("energy"),
                    live_cost,
                    live_value("solar"),
                    live_currency,
                )
                result["active_home_charge"] = active
                result["charges"].insert(0, active)
        result["source_status"] = self.source_status
        result["source_config"] = dict(self.settings)
        history_id = self.settings.get("home_history")
        history_state = self.hass.states.get(history_id) if history_id else None
        result["history_currency_warning"] = (
            history_currency_warning(
                self.ledger,
                history_state.attributes,
                history_state.attributes.get("friendly_name", history_id),
            )
            if history_state
            else None
        )
        return self.cost_recorder.enrich(result)

    async def mutate(self, action, values):
        async with self.lock:
            self.sync_currency()
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
