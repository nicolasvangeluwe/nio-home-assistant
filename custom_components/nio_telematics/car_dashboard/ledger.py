"""Deterministic car ledger. No HA dependency, network calls or destructive edits."""

import json
from copy import deepcopy
from datetime import UTC, datetime
from hashlib import sha256
from math import isfinite
from re import IGNORECASE, fullmatch, match
from uuid import uuid4

# Recognized ISO 4217 units, including retained historical currencies. Source
# parsing is deliberately conservative: unsupported units never acquire HA's
# configured currency. Keep this local; operating the ledger needs no lookup.
SOURCE_CURRENCIES = frozenset(
    "AED AFN ALL AMD ANG AOA ARS AUD AWG AZN BAM BBD BDT BGN BHD BIF BMD BND BOB "
    "BOV BRL BSD BTN BWP BYN BZD CAD CDF CHE CHF CHW CLF CLP CNY COP COU CRC CUC "
    "CUP CVE CZK DJF DKK DOP DZD EGP ERN ETB EUR FJD FKP GBP GEL GHS GIP GMD GNF "
    "GTQ GYD HKD HNL HRK HTG HUF IDR ILS INR IQD IRR ISK JMD JOD JPY KES KGS KHR "
    "KMF KPW KRW KWD KYD KZT LAK LBP LKR LRD LSL LYD MAD MDL MGA MKD MMK MNT "
    "MOP MRU MUR MVR MWK MXN MXV MYR MZN NAD NGN NIO NOK NPR NZD OMR PAB PEN "
    "PGK PHP PKR PLN PYG QAR RON RSD RUB RWF SAR SBD SCR SDG SEK SGD SHP SLE SLL "
    "SOS SRD SSP STN SVC SYP SZL THB TJS TMT TND TOP TRY TTD TWD TZS UAH UGX USD "
    "USN UYI UYU UYW UZS VED VES VND VUV WST XAF XAG XAU XBA XBB XBC XBD XCD "
    "XCG XDR XOF XPD XPF XPT XSU XTS XUA XXX YER ZAR ZMW ZWG ZWL".split()
)


def number(value):
    if isinstance(value, bool) or value is None:
        return None
    try:
        value = float(value)
        return value if isfinite(value) else None
    except (TypeError, ValueError):
        return None


def currency_code(value):
    """Validate the currency discriminator; amounts are never converted."""
    if not isinstance(value, str) or not fullmatch(r"[A-Z]{3}", value):
        raise ValueError("Currency must be a three-letter uppercase code")
    return value


def source_currency(attributes, fallback, *, monetary=True, per_kwh=None):
    """Honor explicit source units; HA's currency is only the no-metadata default."""
    unit = attributes.get("unit_of_measurement")
    unit_currency = None
    if unit not in (None, ""):
        if not isinstance(unit, str):
            raise ValueError("Unsupported monetary source unit")
        unit = unit.strip()
        # A session-history sensor can expose energy or a record count. Those
        # units say nothing about the monetary columns in its session records.
        quantity = unit.lower() in {"kwh", "wh", "mwh", "count", "sessions", "session"}
        parsed = (
            None
            if quantity
            else fullmatch(r"([a-z]{3}|€)(\s*/\s*kwh)?", unit, flags=IGNORECASE)
        )
        if parsed:
            candidate = "EUR" if parsed[1] == "€" else parsed[1].upper()
            if candidate not in SOURCE_CURRENCIES:
                raise ValueError("Unsupported monetary source unit")
            if per_kwh is not None and bool(parsed[2]) != per_kwh:
                raise ValueError("Monetary source unit has the wrong price basis")
            unit_currency = candidate
        else:
            prefix = match(r"[a-z]{3}", unit, flags=IGNORECASE)
            money_looking = (
                any(char in unit for char in "$€£¥¤₹₽₩₺₪₫₴₦฿₱")
                or unit.lower()
                in {
                    "kr",
                    "fr",
                    "zł",
                    "руб",
                    "cents",
                    "rs",
                    "rs.",
                }
                or (prefix is not None and prefix[0].upper() in SOURCE_CURRENCIES)
            )
            if monetary or (money_looking and not quantity):
                raise ValueError("Unsupported monetary source unit")
    if attributes.get("currency") is not None:
        raw = attributes["currency"]
        declared = currency_code(raw.strip().upper() if isinstance(raw, str) else raw)
        if declared not in SOURCE_CURRENCIES:
            raise ValueError("Unsupported source currency")
        if unit_currency is not None and declared != unit_currency:
            raise ValueError("Source currency metadata conflicts with its unit")
        return declared
    return currency_code(unit_currency or fallback)


def provisional_home_charge(ident, start, now, energy, cost, solar, currency="EUR"):
    """Project an identified live EVCC session without archiving it."""
    if not ident or not 0 < start <= now:
        raise ValueError("An active session ID and valid start are required")
    return {
        "id": ident,
        "kind": "home",
        "category": "home",
        "start": start,
        "end": now,
        "kwh": number(energy),
        "cost_eur": number(cost),
        "currency": currency_code(currency),
        "reimbursement_eur": None,
        "benefit_eur": None,
        "solar_pct": number(solar),
        "confirmed": True,
        "ongoing": True,
        "provisional": True,
    }


class Ledger:
    def __init__(self, settings=None, data=None):
        from .const import DEFAULTS

        self.settings = {**DEFAULTS, **(settings or {})}
        self.currency = currency_code(self.settings.get("currency", "EUR"))
        self.data = (
            deepcopy(data)
            if data
            else {
                "trips": [],
                "charges": {},
                "samples": [],
                "last": None,
                "active": None,
                "opening": None,
                "counters": [],
                "preferences": {},
                "revision": 0,
                "parked_losses": [],
            }
        )
        self.data.setdefault("parked_losses", [])
        self.data.setdefault("last_home_charge", None)
        self.data.setdefault("source_transition_at", None)
        self.data.setdefault("source_transition_energy", None)
        self.data.setdefault("initial_capacity_kwh", self.settings["capacity_kwh"])
        self.data.setdefault("pending_epoch", None)
        self.data.setdefault("native_replays", {})
        self.data.setdefault("gap_resolutions", {})
        self.currency_migrated = False
        for charge in self.data["charges"].values():
            if "currency" not in charge:
                charge["currency"] = "EUR"
                self.currency_migrated = True
            currency_code(charge["currency"])
        if "currency" not in self.data["preferences"]:
            self.data["preferences"]["currency"] = "EUR" if data else self.currency
            self.currency_migrated = bool(data)
        currency_code(self.data["preferences"]["currency"])
        if "source_transitions" not in self.data:
            first = self.data["source_transition_at"]
            self.data["source_transitions"] = (
                [
                    {
                        "t": first,
                        "energy": self.data["source_transition_energy"],
                        "capacity_kwh": self.settings["capacity_kwh"],
                    }
                ]
                if first is not None
                else []
            )

    def changed(self):
        self.data["revision"] += 1

    def begin_new_epoch(self, new_settings):
        """Keep archives, but never compare a new source/calibration to the old one."""
        self.close_trip(incomplete=True)
        self.data["last"] = None
        self.data.pop("native_soc_reports", None)
        self.data["pending_epoch"] = {
            "capacity_kwh": new_settings["capacity_kwh"],
            "full_range_km": new_settings["full_range_km"],
        }
        self.changed()

    def record_transition(self, sample):
        """Mark a fresh energy baseline for cost replay and archival boundaries."""
        transition = {
            "t": sample["t"],
            "energy": sample["energy"],
            "capacity_kwh": self.settings["capacity_kwh"],
        }
        self.data["source_transitions"].append(transition)
        if self.data["source_transition_at"] is None:
            self.data["source_transition_at"] = sample["t"]
            self.data["source_transition_energy"] = sample["energy"]

    def observe_native_sources(
        self, odo_t, odo, soc_t, soc, connected=False, connected_since=None
    ):
        """Pair source clocks, never future SoC; persist the small alignment buffer."""
        values = list(map(number, (odo_t, odo, soc_t, soc)))
        if any(v is None for v in values):
            return False
        odo_t, odo, soc_t, soc = values
        if odo <= 0 or not 0 <= soc <= 100:
            return False
        reports = self.data.setdefault("native_soc_reports", [])
        if not any(r["t"] == soc_t and r["soc"] == soc for r in reports):
            reports.append({"t": soc_t, "soc": soc})
            reports.sort(key=lambda r: r["t"])
            self.data["native_soc_reports"] = reports = reports[-2000:]
            self.changed()
        prior = [r for r in reports if 0 <= odo_t - r["t"] <= 180]
        accepted = False
        if prior:
            reading = max(prior, key=lambda r: r["t"])
            accepted = self.ingest(
                odo_t,
                odo,
                None,
                connected,
                soc_pct=reading["soc"],
                home_connected_since=connected_since,
            )
        # The last arrival sample can follow its odometer sample. It updates
        # that endpoint, rather than becoming parked loss or next-trip energy.
        self.reconcile_native_endpoint(
            odo, soc_t, soc, connected=connected, connected_since=connected_since
        )
        return accepted

    def reconcile_native_endpoint(
        self, odo, soc_t, soc, *, connected=False, connected_since=None
    ):
        if connected and (connected_since is None or connected_since <= soc_t):
            return False
        candidates = [
            r
            for r in self.all_trips()
            if r["end_odo"] == odo
            and 0 <= soc_t - r["last_movement"] <= 180
            and r.get("native_alignment_version") == 2
        ]
        if not candidates:
            return False
        trip = max(candidates, key=lambda r: r["end"])
        if soc_t <= trip.get("endpoint_soc_time", trip["end"]):
            return False
        if any(
            charge["kind"] != "dismissed"
            and charge["start"] <= soc_t
            and charge["end"] >= trip["last_movement"]
            for charge in self.data["charges"].values()
        ):
            return False
        energy = soc / 100 * self.settings["capacity_kwh"]
        # Upward events may be charging or BMS corrections. Do not turn them
        # into negative consumption, erase energy, or cross a charge boundary.
        if energy > trip["end_energy"] + 1e-9 or not all(
            row["kwh"] is not None for row in trip["segments"]
        ):
            return False
        delta = trip["end_energy"] - energy
        trip["segments"][-1]["kwh"] += delta
        trip["segments"][-1]["end_energy"] = energy
        trip["end_energy"] = energy
        trip["endpoint_soc_time"] = soc_t
        trip["endpoint_basis"] = "bounded_arrival_estimate"
        if self.data["active"] is trip:
            trip["energy_anchor"] = energy
        last = self.data["last"]
        if last and last["odo"] == odo and last["t"] <= soc_t:
            last.update(energy=energy, soc=soc, endpoint_soc_time=soc_t)
        self.changed()
        return True

    def display_trips(self, tz=UTC):
        """Group short legs without deleting raw trips or moving parked energy."""
        grouped = []
        for raw in sorted(self.all_trips(), key=lambda r: r["start"]):
            trip = deepcopy(raw)
            trip["segments"] = self.accounting_segments(raw)
            trip["leg_ids"] = [raw["id"]]
            previous = grouped[-1] if grouped else None
            same_day = (
                previous
                and datetime.fromtimestamp(previous["end"], tz).date()
                == datetime.fromtimestamp(trip["start"], tz).date()
            )
            blocked = previous and (
                any(
                    c["kind"] != "dismissed"
                    and c["start"] < trip["start"]
                    and c["end"] > previous["end"]
                    for c in self.data["charges"].values()
                )
                or any(
                    previous["end"] <= r["t"] <= trip["start"]
                    for r in self.data["source_transitions"]
                )
            )
            # A short leg is only part of the same journey while the idle
            # interval remains open. Same-day and odometer continuity alone
            # can join separate morning and evening drives.
            gap = (
                trip["start"] - previous.get("last_movement", previous["end"])
                if previous
                else None
            )
            nearby = (
                gap is not None and 0 <= gap <= self.settings["trip_idle_minutes"] * 60
            )
            parked_between = previous and any(
                (number(loss.get("kwh")) or 0) > 0
                and loss["start"] < trip["start"]
                and loss["end"] > previous["end"]
                for loss in self.data["parked_losses"]
            )
            if (
                previous
                and previous["distance_km"] < 5
                and same_day
                and nearby
                and previous["end_odo"] == trip["start_odo"]
                and not blocked
                and not parked_between
            ):
                previous["segments"].extend(trip["segments"])
                previous["distance_km"] += trip["distance_km"]
                previous["leg_ids"].extend(trip["leg_ids"])
                previous.update(
                    end=trip["end"],
                    last_movement=trip["last_movement"],
                    end_odo=trip["end_odo"],
                    end_energy=trip["end_energy"],
                    complete=previous["complete"] and trip["complete"],
                )
                if self.data["active"] and raw["id"] == self.data["active"]["id"]:
                    previous["id"] = raw["id"]
            else:
                grouped.append(trip)
        return grouped

    def energy(self, range_km):
        return max(
            0,
            min(
                self.settings["capacity_kwh"],
                range_km
                / self.settings["full_range_km"]
                * self.settings["capacity_kwh"],
            ),
        )

    def classify_recorded_intervals(self):
        """Correct legacy trip energy from retained evidence, preserving trip IDs."""
        samples = sorted(self.data["samples"], key=lambda r: r["t"])
        for trip in self.all_trips():
            if trip.get("native_alignment_version") == 2:
                continue
            # Archived range-based trips are immutable after migration.
            if (
                self.data["source_transition_at"] is not None
                and trip["start"] < self.data["source_transition_at"]
            ):
                continue
            rows = [r for r in samples if trip["start"] <= r["t"] <= trip["end"]]
            # Native SoC needs distance-window replay, not the legacy
            # adjacent-sample range classifier.
            if any(r.get("energy_source") == "native_soc" for r in rows):
                continue
            if (
                len(rows) < 2
                or rows[0]["t"] != trip["start"]
                or rows[-1]["t"] != trip["end"]
            ):
                continue
            segments, losses = [], []
            valid = True
            for old, new in zip(rows, rows[1:], strict=False):
                if old.get("energy_source", "range_estimate") != new.get(
                    "energy_source", "range_estimate"
                ):
                    valid = False
                    break
                distance, elapsed = new["odo"] - old["odo"], new["t"] - old["t"]
                delta = old["energy"] - new["energy"]
                charging = (
                    old.get("home_connected")
                    or new.get("home_connected")
                    or any(
                        c["kind"] != "dismissed"
                        and c["start"] < new["t"]
                        and c["end"] > old["t"]
                        for c in self.data["charges"].values()
                    )
                )
                if (
                    distance < 0
                    or distance > elapsed / 3600 * 250 + 5
                    or charging
                    or delta < 0
                ):
                    valid = False
                    break
                if distance > 0:
                    segments.append(
                        {
                            "start": old["t"],
                            "end": new["t"],
                            "km": distance,
                            "kwh": delta,
                            "complete": True,
                            "start_energy": old["energy"],
                            "end_energy": new["energy"],
                        }
                    )
                elif delta > 0:
                    losses.append(
                        {
                            "start": old["t"],
                            "end": new["t"],
                            "kwh": delta,
                            "end_energy": new["energy"],
                            "complete": True,
                        }
                    )
            if (
                not valid
                or not segments
                or abs(sum(s["km"] for s in segments) - trip["distance_km"]) > 1e-6
            ):
                continue
            corrected = dict(
                trip,
                segments=segments,
                complete=True,
                end=segments[-1]["end"],
                last_movement=segments[-1]["end"],
                end_energy=segments[-1]["end_energy"],
            )
            if corrected != trip:
                trip.update(corrected)
                self.changed()
            for loss in losses:
                if not any(
                    r["start"] == loss["start"] and r["end"] == loss["end"]
                    for r in self.data["parked_losses"]
                ):
                    self.data["parked_losses"].append(loss)
                    self.changed()

    def close_trip(self, incomplete=False):
        trip = self.data["active"]
        if not trip:
            return
        last = self.data["last"]
        if (
            last
            and last.get("energy_source") == "native_soc"
            and last["t"] > trip["last_movement"]
            and last["odo"] == trip["end_odo"]
            and last["energy"] < trip["end_energy"]
            and not last.get("home_connected")
            and not any(
                charge["kind"] != "dismissed"
                and charge["start"] < last["t"]
                and charge["end"] > trip["last_movement"]
                for charge in self.data["charges"].values()
            )
            and all(segment["kwh"] is not None for segment in trip["segments"])
        ):
            # Only after the trip has actually closed can a stationary SoC
            # decrease be separated from a short traffic stop.
            self.data["parked_losses"].append(
                {
                    "start": trip["last_movement"],
                    "end": last["t"],
                    "kwh": trip["end_energy"] - last["energy"],
                    "end_energy": last["energy"],
                    "complete": True,
                }
            )
        if incomplete:
            trip["complete"] = False
        if any(segment["kwh"] is None for segment in trip["segments"]):
            trip["complete"] = False
        trip.pop("energy_anchor", None)
        self.data["trips"].append(trip)
        self.data["active"] = None
        self.changed()

    def tick(self, now):
        trip = self.data["active"]
        if (
            trip
            and now - trip.get("last_movement", trip["end"])
            >= self.settings["trip_idle_minutes"] * 60
        ):
            self.close_trip()

    def ingest(
        self,
        timestamp,
        odometer,
        range_km,
        home_connected=False,
        *,
        soc_pct=None,
        home_connected_since=None,
    ):
        t, odo, km = map(number, (timestamp, odometer, range_km))
        soc = number(soc_pct)
        if (
            t is None
            or odo is None
            or odo <= 0
            or (km is not None and not 0 <= km <= self.settings["full_range_km"] * 1.1)
        ):
            return False
        if soc_pct is not None and (soc is None or not 0 <= soc <= 100):
            return False
        if soc is None and km is None:
            return False
        source = "native_soc" if soc is not None else "range_estimate"
        energy = (
            soc / 100 * self.settings["capacity_kwh"]
            if soc is not None
            else self.energy(km)
        )
        sample = {
            "t": t,
            "odo": odo,
            "range": km,
            "energy": energy,
            "energy_source": source,
            "home_connected": home_connected,
        }
        if soc is not None:
            sample["soc"] = soc
        old = self.data["last"]
        if old and t <= old["t"]:
            return False
        self.tick(t)
        arrival = bool(
            old
            and source == "native_soc"
            and home_connected
            and number(home_connected_since) is not None
            and old["t"] <= home_connected_since <= t
            and t - home_connected_since <= 180
            and 0 < odo - old["odo"] <= 2
            and energy <= old["energy"]
        )
        departure = bool(
            old
            and source == "native_soc"
            and not home_connected
            and old.get("home_connected")
            and number(home_connected_since) is not None
            and old["t"] <= home_connected_since <= t
            and t - home_connected_since <= 180
            and 0 < odo - old["odo"] <= 2
            and energy <= old["energy"]
        )
        if home_connected and not arrival:
            self.close_trip()
        if arrival and self.data["active"] is None and self.data["trips"]:
            previous = self.data["trips"][-1]
            if (
                previous["end_odo"] == old["odo"]
                and t - previous["last_movement"] <= 180
                and previous["end"] <= home_connected_since
            ):
                self.data["active"] = self.data["trips"].pop()
                self.data["active"]["energy_anchor"] = previous["end_energy"]
        if old and old.get("energy_source", "range_estimate") != source:
            # The two energy estimates have different baselines. Never turn
            # their difference into a trip, stationary loss or charge.
            self.close_trip(incomplete=True)
            self.record_transition(sample)
            self.data["last"] = sample
            self.data["samples"].append(sample)
            self.data["samples"] = self.data["samples"][-2000:]
            self.changed()
            return True
        if not old:
            if self.data["opening"] is None:
                self.data["opening"] = deepcopy(sample)
            elif self.data["pending_epoch"] is not None:
                self.record_transition(sample)
                self.data["pending_epoch"] = None
            if not self.data["counters"]:
                self.data["counters"] = [
                    {"id": "trip-a", "name": "Trip A", "start": t},
                    {"id": "trip-b", "name": "Trip B", "start": t},
                ]
        else:
            distance, elapsed = odo - old["odo"], t - old["t"]
            delta = old["energy"] - sample["energy"]
            gap = elapsed > self.settings["max_gap_minutes"] * 60
            if distance < 0 or distance > elapsed / 3600 * 250 + 5:
                self.close_trip(incomplete=True)
                sample["discontinuity"] = True
            elif distance > 0:
                trip = self.data["active"]
                if trip is None:
                    trip = {
                        "id": "trip-" + uuid4().hex,
                        "start": old["t"],
                        "end": t,
                        "start_odo": old["odo"],
                        "end_odo": odo,
                        "start_energy": old["energy"],
                        "end_energy": sample["energy"],
                        "distance_km": 0.0,
                        "segments": [],
                        "complete": True,
                    }
                    self.data["active"] = trip
                    if source == "native_soc":
                        trip["native_alignment_version"] = 2
                        trip["energy_anchor"] = old["energy"]
                if source == "native_soc":
                    # Unchanged-distance reports are real samples, but their
                    # energy must stay with the next movement window until
                    # the trip is closed. A 0.5% upward correction is likewise
                    # held until a later reading establishes the net change.
                    delta = trip.get("energy_anchor", old["energy"]) - sample["energy"]
                charging = (
                    home_connected
                    or old.get("home_connected")
                    or any(
                        c["kind"] != "dismissed"
                        and c["start"] < t
                        and c["end"] > old["t"]
                        for c in self.data["charges"].values()
                    )
                )
                if arrival or departure:
                    # A bounded cable transition is a movement endpoint, not
                    # evidence that the complete driving window was charging.
                    charging = False
                complete = (
                    delta >= 0 and not charging and not (gap and source == "native_soc")
                )
                invalid_reason = (
                    "charging"
                    if charging
                    else "gap"
                    if gap and source == "native_soc"
                    else "native_rebound"
                    if delta < 0
                    else None
                )
                segment = {
                    "start": trip.get("last_movement", old["t"]),
                    "end": t,
                    "km": distance,
                    "kwh": delta if complete else None,
                    "complete": complete,
                    "sparse": gap,
                    "invalid_reason": invalid_reason,
                    "start_energy": old["energy"],
                    "end_energy": sample["energy"],
                }
                trip["segments"].append(segment)
                if source == "native_soc" and invalid_reason == "gap":
                    # Resume from this observed endpoint, never price or count
                    # the unavailable gap again in the next movement window.
                    trip["energy_anchor"] = sample["energy"]
                if source == "native_soc" and complete:
                    pending = [segment]
                    for prior in reversed(trip["segments"][:-1]):
                        if (
                            prior["kwh"] is not None
                            or prior.get("invalid_reason") != "native_rebound"
                        ):
                            break
                        pending.append(prior)
                    if len(pending) > 1:
                        total_km = sum(row["km"] for row in pending)
                        for row in pending:
                            row["kwh"] = delta * row["km"] / total_km
                            row["complete"] = True
                            row["native_correction_resolved"] = True
                    trip["energy_anchor"] = sample["energy"]
                trip["distance_km"] += distance
                trip.update(
                    end=t,
                    last_movement=t,
                    end_odo=odo,
                    end_energy=sample["energy"],
                    complete=trip["complete"]
                    and (
                        complete
                        or (source == "native_soc" and not charging and not gap)
                    ),
                )
            elif delta < -self.energy(2) and not (
                source == "native_soc"
                and -delta <= self.settings["capacity_kwh"] * 0.01
            ):
                home_overlap = (
                    home_connected
                    or old.get("home_connected")
                    or any(
                        c["kind"] == "home" and c["start"] <= t and c["end"] >= old["t"]
                        for c in self.data["charges"].values()
                    )
                )
                if home_overlap:
                    self.close_trip()
                    self.data["last_home_charge"] = t
                    self.data["last"] = sample
                    self.data["samples"].append(sample)
                    self.data["samples"] = self.data["samples"][-2000:]
                    self.changed()
                    return True
                # A range increase is only a candidate, never proven public charging.
                self.close_trip()
                nearby = [
                    c
                    for c in self.data["charges"].values()
                    if c["kind"] == "candidate"
                    and t - c["end"] < 3600
                    and c.get("odo") == odo
                ]
                if nearby:
                    c = max(nearby, key=lambda x: x["end"])
                    c["end"] = t
                    c["estimated_kwh"] += -delta
                    c["kwh"] = c["estimated_kwh"]
                else:
                    ident = "public-" + uuid4().hex
                    self.data["charges"][ident] = {
                        "id": ident,
                        "kind": "candidate",
                        "category": "other",
                        "start": old["t"],
                        "end": t,
                        "odo": odo,
                        "kwh": -delta,
                        "estimated_kwh": -delta,
                        "cost_eur": None,
                        "price_eur_kwh": None,
                        "currency": self.currency,
                        "confirmed": False,
                        "energy_basis": source,
                        "cost_basis": "unknown",
                    }
            elif (
                delta > 0
                and not home_connected
                and not (source == "native_soc" and self.data["active"] is not None)
            ):
                # Classification follows measured distance, even during short stops.
                self.data["parked_losses"].append(
                    {
                        "start": old["t"],
                        "end": t,
                        "kwh": delta,
                        "end_energy": sample["energy"],
                        "complete": True,
                    }
                )
        self.data["last"] = sample
        if arrival:
            self.close_trip()
        # Small samples only; trips and charges are never age-pruned.
        self.data["samples"].append(sample)
        self.data["samples"] = self.data["samples"][-2000:]
        self.changed()
        return True

    def import_home(self, rows, active_session_id=None, currency=None):
        currency = currency_code(self.currency if currency is None else currency)
        changed = False
        active_id = (
            "home-" + str(active_session_id) if active_session_id is not None else None
        )
        if active_id in self.data["charges"]:
            active = self.data["charges"][active_id]
            if not active.get("ongoing"):
                active["ongoing"] = True
                changed = True
        for row in rows:
            if not isinstance(row, (list, tuple)) or len(row) < 8:
                continue
            start, end, kwh = map(number, row[1:4])
            if None in (start, end, kwh) or kwh <= 0 or end < start:
                continue
            ident = "home-" + str(row[0])
            if ident == active_id:
                continue
            existing = self.data["charges"].get(ident, {})
            charge = {
                "id": ident,
                "kind": "home",
                "category": "home",
                "start": start,
                "end": end,
                "kwh": kwh,
                "cost_eur": number(row[5]),
                "currency": currency,
                "reimbursement_eur": number(row[6]),
                "benefit_eur": number(row[7]),
                "solar_pct": number(row[4]),
                "confirmed": True,
                "energy_basis": "charger_meter",
                "cost_basis": "evcc_energy_and_foregone_export",
            }
            if existing and existing.get("currency", "EUR") != currency:
                # A source/configuration change cannot relabel or replace an
                # archived amount. Preserve every monetary component together.
                for key in (
                    "currency",
                    "cost_eur",
                    "reimbursement_eur",
                    "benefit_eur",
                    "price_eur_kwh",
                    "cost_basis",
                    "manual_cost",
                ):
                    if key in existing:
                        charge[key] = existing[key]
                charge["cost_currency_conflict"] = True
            if existing.get("manual_cost"):
                charge.update(
                    {k: existing[k] for k in ("manual_cost", "cost_eur", "cost_basis")}
                )
                if existing.get("price_eur_kwh") is not None:
                    charge["price_eur_kwh"] = existing["price_eur_kwh"]
                    if charge["cost_basis"] == "entered_rate":
                        charge["cost_eur"] = kwh * existing["price_eur_kwh"]
            if charge != existing:
                self.data["charges"][ident] = charge
                changed = True
        if changed:
            self.changed()

    def edit_charge(
        self,
        ident,
        *,
        price=None,
        receipt=None,
        kwh=None,
        category=None,
        confirmed=True,
        currency=None,
    ):
        charge = self.data["charges"][ident]
        currency = currency_code(
            charge.get("currency", "EUR") if currency is None else currency
        )
        currency_changed = currency != charge.get("currency", "EUR")
        if any(
            raw is not None and number(raw) is None for raw in (price, receipt, kwh)
        ):
            raise ValueError("Amounts must be finite numbers")
        price, receipt, kwh = map(number, (price, receipt, kwh))
        if any(x is not None and x < 0 for x in (price, receipt)) or (
            kwh is not None and kwh <= 0
        ):
            raise ValueError("Amounts must be nonnegative; energy must be positive")
        if category and category not in ("home", "work", "supercharger", "other"):
            raise ValueError("Unknown charging category")
        if kwh is not None:
            charge.update(kwh=kwh, energy_basis="receipt")
            if (
                price is None
                and receipt is None
                and charge.get("cost_basis") == "entered_rate"
            ):
                price = charge.get("price_eur_kwh")
                if currency_changed:
                    price = None
        if currency_changed:
            # Selecting a new unit without entering replacement amounts clears
            # the old monetary values; it never relabels their numbers.
            charge.update(
                currency=currency,
                cost_eur=None,
                price_eur_kwh=None,
                reimbursement_eur=None,
                benefit_eur=None,
                cost_basis="unknown",
                manual_cost=True,
            )
            charge.pop("cost_currency_conflict", None)
        if price is not None or receipt is not None:
            charge.update(
                cost_eur=receipt if receipt is not None else price * charge["kwh"],
                price_eur_kwh=price,
                cost_basis="receipt" if receipt is not None else "entered_rate",
                manual_cost=True,
                currency=currency,
            )
            charge.pop("cost_currency_conflict", None)
            if currency_changed:
                charge["reimbursement_eur"] = charge["benefit_eur"] = None
        if category:
            charge["category"] = category
        charge["confirmed"] = confirmed
        if charge["kind"] == "candidate" and confirmed:
            charge["kind"] = "public"
        self.changed()

    def add_charge(self, start, end, kwh, **kwargs):
        start, end, kwh = map(number, (start, end, kwh))
        if None in (start, end, kwh) or start > end or kwh <= 0:
            raise ValueError("Valid charging times and positive energy required")
        ident = "manual-" + uuid4().hex
        self.data["charges"][ident] = {
            "id": ident,
            "kind": "public",
            "category": "other",
            "start": start,
            "end": end,
            "kwh": kwh,
            "cost_eur": None,
            "currency": currency_code(
                self.currency if kwargs.get("currency") is None else kwargs["currency"]
            ),
            "confirmed": True,
            "energy_basis": "manual",
            "cost_basis": "unknown",
        }
        try:
            self.edit_charge(ident, **kwargs)
        except Exception:
            self.data["charges"].pop(ident)
            raise
        return ident

    def dismiss_candidate(self, ident):
        charge = self.data["charges"][ident]
        if charge["kind"] != "candidate":
            raise ValueError("Only inferred candidates can be dismissed")
        # Audit retained, never physically delete history.
        charge["kind"] = "dismissed"
        self.changed()

    def all_trips(self):
        return self.data["trips"] + (
            [self.data["active"]] if self.data["active"] else []
        )

    def accounting_segments(self, trip, apply_resolutions=True):
        """Exclude a proven legacy gap-anchor overlap without changing archives."""
        rows = deepcopy(trip["segments"])
        for previous, row in zip(rows, rows[1:], strict=False):
            if (
                trip.get("native_alignment_version", 0) < 1
                or previous.get("invalid_reason") != "gap"
                or row.get("kwh") is None
            ):
                continue
            before, after, end = map(
                number,
                (
                    previous.get("start_energy"),
                    previous.get("end_energy"),
                    row.get("end_energy"),
                ),
            )
            if (
                None not in (before, after, end)
                and row["start"] == previous["end"]
                and before > after >= end >= 0
                and row.get("complete", True)
                and not row.get("invalid_reason")
                and abs(row["kwh"] - (before - end)) <= 1e-6
            ):
                row.update(
                    kwh=None, complete=False, invalid_reason="legacy_gap_overlap"
                )
        for original, row in zip(trip["segments"], rows, strict=True):
            if row.get("invalid_reason") not in ("gap", "legacy_gap_overlap"):
                continue
            ident = (
                "gap-"
                + sha256(
                    json.dumps([trip["id"], row["start"], row["end"]]).encode()
                ).hexdigest()[:24]
            )
            fingerprint = sha256(
                json.dumps(
                    {
                        "trip_id": trip["id"],
                        "segment": original,
                        "source": trip.get("source"),
                        "native_alignment_version": trip.get(
                            "native_alignment_version"
                        ),
                        "capacity_kwh": self.data["initial_capacity_kwh"],
                        "transitions": [
                            t
                            for t in self.data["source_transitions"]
                            if t["t"] <= row["end"]
                        ],
                    },
                    sort_keys=True,
                ).encode()
            ).hexdigest()
            saved = self.data["gap_resolutions"].get(ident)
            resolution = (
                (saved["status"] if saved["fingerprint"] == fingerprint else "stale")
                if saved
                else "open"
            )
            row.update(
                gap_id=ident,
                gap_fingerprint=fingerprint,
                gap_resolution=resolution,
                raw_trip_id=trip["id"],
            )
            if resolution == "manual":
                row.update(
                    gap_energy_kwh=saved["energy_kwh"],
                    gap_cost=saved.get("cost"),
                    gap_currency=saved["currency"],
                )
                if apply_resolutions:
                    row.update(
                        kwh=saved["energy_kwh"],
                        complete=True,
                        manual_gap_reconciled=True,
                        energy_basis="manual_gap",
                    )
        return rows

    def unaccounted_intervals(self):
        """Expose original gap identities and user choices, never inferred usage."""
        result = []
        for trip in self.all_trips():
            for row in self.accounting_segments(trip, apply_resolutions=False):
                if "gap_id" not in row:
                    continue
                start, end = (
                    number(row.get("start_energy")),
                    number(row.get("end_energy")),
                )
                result.append(
                    {
                        "id": row["gap_id"],
                        "fingerprint": row["gap_fingerprint"],
                        "trip_id": trip["id"],
                        "start": row["start"],
                        "end": row["end"],
                        "km": row["km"],
                        "start_energy": start,
                        "end_energy": end,
                        "battery_change_kwh": end - start
                        if None not in (start, end)
                        else None,
                        "resolution": row["gap_resolution"],
                        "energy_kwh": row.get("gap_energy_kwh"),
                        "cost": row.get("gap_cost"),
                        "currency": row.get("gap_currency", self.currency),
                    }
                )
        return result

    def resolve_gap(
        self, ident, fingerprint, status, energy_kwh=None, cost=None, currency=None
    ):
        """Replace one reversible user overlay; raw evidence and charges stay intact."""
        interval = next(
            (r for r in self.unaccounted_intervals() if r["id"] == ident), None
        )
        saved = self.data["gap_resolutions"].get(ident)
        if (
            status == "open"
            and interval is None
            and saved
            and saved["fingerprint"] == fingerprint
        ):
            self.data["gap_resolutions"].pop(ident)
            self.changed()
            return
        if interval is None or interval["fingerprint"] != fingerprint:
            raise ValueError("The gap changed; refresh before saving")
        if status not in ("manual", "ignored", "open"):
            raise ValueError("Unknown gap resolution")
        if status != "manual" and any(
            v is not None for v in (energy_kwh, cost, currency)
        ):
            raise ValueError("Only manual completion accepts usage or cost")
        record = {"fingerprint": fingerprint, "status": status}
        if status == "manual":
            energy = number(energy_kwh)
            actual_cost = number(cost)
            if (
                energy is None
                or energy < 0
                or (cost is not None and actual_cost is None)
            ):
                raise ValueError(
                    "Enter finite nonnegative usage and an optional finite cost"
                )
            record.update(
                energy_kwh=energy,
                cost=actual_cost,
                currency=currency_code(self.currency if currency is None else currency),
            )
        if status == "open":
            self.data["gap_resolutions"].pop(ident, None)
        else:
            self.data["gap_resolutions"][ident] = record
        self.changed()

    def cost_segments(self):
        """Replay booked battery value; missing trip allocation is never a charge.

        A discharge-only telemetry gap reconciles the inventory quantity to its
        observed endpoint while retaining an already fully known booked price.
        Its own energy/cost stay unknown. Unknown prices and actual charging or
        source boundaries cannot acquire that price through this convention.
        """
        opening = self.data["opening"]
        if not opening:
            return []
        stock = opening["energy"]
        capacity = self.data["initial_capacity_kwh"]
        initial_price = number(self.data["preferences"].get("opening_price_eur_kwh"))
        if self.data["preferences"].get("currency", "EUR") != self.currency:
            initial_price = None
        known_energy = stock if initial_price is not None else 0.0
        value = stock * (initial_price or 0)
        events = []
        for charge in self.data["charges"].values():
            if (
                charge["kind"] != "dismissed"
                and not charge.get("ongoing")
                and charge["end"] > opening["t"]
            ):
                events.append((charge["end"], 0, "charge", charge))
        for trip in self.all_trips():
            for segment in self.accounting_segments(trip, apply_resolutions=False):
                events.append((segment["end"], 1, "trip", segment))
        for loss in self.data["parked_losses"]:
            events.append((loss["end"], 1, "parked", loss))
        for transition in self.data["source_transitions"]:
            events.append((transition["t"], -1, "source_transition", transition))
        result = []
        for _, _, kind, row in sorted(events, key=lambda x: (x[0], x[1])):
            if kind == "source_transition":
                stock = row["energy"]
                capacity = row["capacity_kwh"]
                known_energy = value = 0.0
            elif kind == "charge":
                kwh = row["kwh"]
                # Wall-to-battery losses are unknown; allocation is approximate.
                if stock + kwh > capacity:
                    kwh = max(0, capacity - stock)
                cost = (
                    row.get("cost_eur")
                    if (
                        row.get("confirmed")
                        and row.get("currency", "EUR") == self.currency
                    )
                    else None
                )
                stock += kwh
                if cost is not None:
                    known_energy += kwh
                    value += cost
            else:
                energy = row["kwh"]
                complete = (
                    energy is not None
                    and stock > 0
                    and known_energy >= stock - 1e-6
                    and energy <= stock + 1e-6
                )
                price = value / stock if stock > 0 else None
                start_energy = number(row.get("start_energy"))
                end_energy = number(row.get("end_energy"))
                can_carry = (
                    energy is None
                    and row.get("invalid_reason") in ("gap", "legacy_gap_overlap")
                    and None not in (start_energy, end_energy)
                    and 0 <= end_energy <= start_energy <= capacity
                    # Endpoint reconciliation can remove booked stock, never
                    # introduce unrecorded energy with an invented known price.
                    and start_energy <= stock + 1e-6
                    and end_energy <= stock + 1e-6
                    and stock > 0
                    and known_energy >= stock - 1e-6
                    and not any(
                        c["kind"] != "dismissed"
                        and c["start"] < row["end"]
                        and c["end"] > row["start"]
                        for c in self.data["charges"].values()
                    )
                    and not any(
                        row["start"] <= t["t"] <= row["end"]
                        for t in self.data["source_transitions"]
                    )
                )
                if kind == "trip":
                    projected = {
                        **row,
                        "cost_eur": energy * price if complete else None,
                        "currency": self.currency,
                    }
                    if row.get("gap_resolution") == "manual":
                        manual_energy, actual_cost = (
                            row["gap_energy_kwh"],
                            row["gap_cost"],
                        )
                        own_currency = row["gap_currency"]
                        booked = (
                            manual_energy * price
                            if can_carry
                            and manual_energy <= start_energy - end_energy + 1e-6
                            and manual_energy <= stock + 1e-6
                            else None
                        )
                        projected.update(
                            kwh=manual_energy,
                            complete=True,
                            manual_gap_reconciled=True,
                            energy_basis="manual_gap",
                            cost_eur=(
                                actual_cost if own_currency == self.currency else None
                            )
                            if actual_cost is not None
                            else booked,
                            currency=own_currency
                            if actual_cost is not None
                            else self.currency,
                        )
                    result.append(projected)
                if energy is None:
                    # Reconcile ORIGINAL gap stock exactly once. Manual usage
                    # and cost allocate the interval; neither is a new purchase
                    # or a second battery depletion.
                    stock = end_energy if end_energy is not None else capacity
                    if can_carry:
                        known_energy = stock
                        value = stock * price
                    else:
                        known_energy = value = 0.0
                elif stock > 0:
                    fraction = max(0, (stock - energy) / stock)
                    stock *= fraction
                    known_energy *= fraction
                    value *= fraction
        return result

    def statistics(self, start, end, window_km=None, trip=None, native_only=False):
        selected = {(r["start"], r["end"]) for r in trip["segments"]} if trip else None
        native_segments = (
            {
                (r["start"], r["end"], r["km"])
                for t in self.all_trips()
                if t.get("native_alignment_version", 0) >= 1
                or t.get("source") in ("native_source_replay", "native_soc")
                for r in t["segments"]
            }
            if native_only
            else None
        )
        seen = set()
        segments = []
        for row in self.cost_segments():
            key = (row["start"], row["end"], row["km"])
            if (
                not start <= row["end"] <= end
                or (selected is not None and key[:2] not in selected)
                or (native_segments is not None and key not in native_segments)
                or (native_only and row.get("manual_gap_reconciled"))
                or key in seen
            ):
                continue
            seen.add(key)
            segments.append(row)

        def valid_energy(row):
            km, kwh = number(row.get("km")), number(row.get("kwh"))
            return (
                row.get("complete", True)
                and (
                    not row.get("invalid_reason")
                    or row.get("native_correction_resolved")
                    or row.get("manual_gap_reconciled")
                )
                and km is not None
                and km > 0
                and kwh is not None
                and kwh >= 0
            )

        if window_km is not None:
            result, remaining = [], window_km
            for row in reversed(segments):
                if remaining <= 0:
                    break
                if not valid_energy(row):
                    continue
                portion = min(remaining, row["km"])
                scale = portion / row["km"]
                result.append(
                    {
                        **row,
                        "km": portion,
                        "kwh": row["kwh"] * scale,
                        "cost_eur": row["cost_eur"] * scale
                        if row["cost_eur"] is not None
                        else None,
                    }
                )
                remaining -= portion
            segments = list(reversed(result))
        gaps = [r for r in segments if "gap_id" in r]
        unaccounted = [r for r in gaps if r["gap_resolution"] != "manual"]
        changes = [
            (number(r.get("start_energy")), number(r.get("end_energy")))
            for r in unaccounted
        ]
        unaccounted_change = (
            sum(b - a for a, b in changes)
            if all(None not in pair for pair in changes)
            else None
        )
        distance = sum(r["km"] for r in segments)
        known = [r for r in segments if valid_energy(r)]
        known_distance = sum(r["km"] for r in known)
        priced = [r for r in known if number(r.get("cost_eur")) is not None]
        priced_distance = sum(r["km"] for r in priced)
        energy_ok = bool(segments) and len(known) == len(segments)
        cost_ok = bool(segments) and len(priced) == len(segments)
        energy = sum(r["kwh"] for r in known) if known else None
        cost = sum(r["cost_eur"] for r in priced) if priced else None
        charges = [
            c
            for c in self.data["charges"].values()
            if c["kind"] != "dismissed"
            and not c.get("ongoing")
            and start <= c["end"] <= end
        ]
        confirmed = [c for c in charges if c.get("confirmed")]
        compatible = [c for c in confirmed if c.get("currency", "EUR") == self.currency]
        mismatches = sum(c.get("currency", "EUR") != self.currency for c in confirmed)
        mismatches += sum(
            r.get("manual_gap_reconciled", False)
            and r.get("gap_cost") is not None
            and r.get("gap_currency") != self.currency
            for r in segments
        )
        charged = sum(c["kwh"] for c in confirmed)
        known_spend = sum(
            c["cost_eur"] for c in compatible if c.get("cost_eur") is not None
        )
        complete_spend = all(
            c.get("confirmed")
            and c.get("cost_eur") is not None
            and c.get("currency", "EUR") == self.currency
            for c in charges
        )
        categories = {}
        for category in ("home", "work", "supercharger", "other"):
            rows = [c for c in confirmed if c["category"] == category]
            if rows:
                total = sum(c["kwh"] for c in rows)
                complete = all(
                    c.get("cost_eur") is not None
                    and c.get("currency", "EUR") == self.currency
                    for c in rows
                )
                spend = sum(c["cost_eur"] for c in rows) if complete else None
                categories[category] = {
                    "currency": self.currency,
                    "currency_mismatch_count": sum(
                        c.get("currency", "EUR") != self.currency for c in rows
                    ),
                    "kwh": total,
                    "cost_eur": spend,
                    "price_eur_kwh": spend / total
                    if spend is not None and total
                    else None,
                }
        return {
            "currency": self.currency,
            "currency_mismatch_count": mismatches,
            "unaccounted_distance_km": sum(r["km"] for r in unaccounted),
            "unaccounted_battery_change_kwh": unaccounted_change,
            "unaccounted_intervals": len(unaccounted),
            "ignored_gap_count": sum(r["gap_resolution"] == "ignored" for r in gaps),
            "manual_gap_count": sum(r["gap_resolution"] == "manual" for r in gaps),
            "distance_km": distance,
            "consumption_distance_km": known_distance,
            "cost_distance_km": priced_distance,
            "used_kwh": energy,
            "parked_loss_estimate_kwh": sum(
                r["kwh"]
                for r in self.data["parked_losses"]
                if start <= r["end"] <= end and r["complete"]
            ),
            "soc_used_pct": energy / self.settings["capacity_kwh"] * 100
            if energy is not None
            else None,
            "consumption_kwh_100km": energy / known_distance * 100
            if energy is not None and known_distance
            else None,
            "driving_cost_eur": cost,
            "cost_eur_100km": cost / priced_distance * 100
            if cost is not None and priced_distance
            else None,
            "charged_kwh": charged,
            "known_spend_eur": known_spend,
            "spend_eur": known_spend if complete_spend else None,
            "price_eur_kwh": known_spend / charged
            if complete_spend and charged
            else None,
            "missing_prices": sum(c.get("cost_eur") is None for c in charges),
            "unconfirmed_charges": sum(not c.get("confirmed") for c in charges),
            "energy_complete": energy_ok,
            "cost_complete": cost_ok,
            "categories": categories,
            "segments": segments,
        }

    def counter(self, name, now, ident=None):
        name = str(name).strip()
        if not name or len(name) > 60:
            raise ValueError("Counter name required, up to 60 characters")
        if ident:
            item = next(c for c in self.data["counters"] if c["id"] == ident)
            item.update(name=name, start=now)
        else:
            self.data["counters"].append(
                {"id": uuid4().hex, "name": name, "start": now}
            )
        self.changed()

    def recover_history(self, samples, now):
        """One-time replay of verified Recorder samples into an empty trip ledger."""
        if self.data.get("recovery_completed"):
            return
        if self.data["opening"] or self.all_trips():
            raise ValueError("History recovery requires an empty trip ledger")
        if not isinstance(samples, list) or not 2 <= len(samples) <= 2000:
            raise ValueError("Supply 2–2000 chronological recorded samples")
        previous = 0
        for sample in samples:
            if not isinstance(sample, dict):
                raise ValueError("Invalid recorded sample")
            t, odo, km = map(
                number, (sample.get("t"), sample.get("odo"), sample.get("range"))
            )
            if (
                None in (t, odo, km)
                or t <= previous
                or t > now
                or odo <= 0
                or not 0 <= km <= self.settings["full_range_km"] * 1.1
            ):
                raise ValueError("Invalid chronological recorded sample")
            if not isinstance(sample.get("home_connected"), bool):
                raise ValueError("Recorded connection state required")
            previous = t
        for sample in samples:
            self.ingest(
                sample["t"], sample["odo"], sample["range"], sample["home_connected"]
            )
        self.tick(now)
        for trip in self.all_trips():
            trip["source"] = "recorder_recovery"
        self.data["recovery_completed"] = True
        self.changed()

    def repair_native_trip(self, ident, reports, now, merge_tail_id=None):
        """Replace a native trip (and optionally its false short tail) from reports.

        The caller supplies timestamp-aligned, fresh odometer/SoC evidence.
        All other trips, charges, old samples and source transitions stay intact.
        The coordinator persists this mutation atomically with the HA Store.
        """
        was_active = bool(self.data["active"] and self.data["active"]["id"] == ident)
        old = (
            self.data["active"]
            if was_active
            else next((r for r in self.data["trips"] if r["id"] == ident), None)
        )
        tail = (
            next((r for r in self.data["trips"] if r["id"] == merge_tail_id), None)
            if merge_tail_id
            else None
        )
        if (
            old is None
            or not isinstance(reports, list)
            or not 2 <= len(reports) <= 1000
        ):
            raise ValueError("A saved trip and 2–1000 source reports are required")
        if was_active and merge_tail_id:
            raise ValueError("An active trip cannot merge a saved tail")
        if merge_tail_id and tail is None:
            # A repeated, already-applied repair must not remove anything else.
            previous = self.data["native_replays"].get(ident, {})
            if merge_tail_id in previous.get("merged_ids", []):
                return False
            raise ValueError("The selected tail trip does not exist")
        if tail and (
            tail is old
            or old["end"] > tail["start"]
            or tail["start"] - old["end"] > 15 * 60
            or old["end_odo"] != tail["start_odo"]
            or not 0 < tail["distance_km"] <= 2
            or tail.get("complete", True)
            or any(
                trip not in (old, tail)
                and old["start"] < trip["end"]
                and trip["start"] < tail["end"]
                for trip in self.data["trips"]
            )
        ):
            raise ValueError("Tail is not an adjacent incomplete odometer update")
        if not any(
            sample.get("energy_source") == "native_soc"
            and old["start"] <= sample["t"] <= old["end"]
            for sample in self.data["samples"]
        ):
            raise ValueError("Trip is not a recorded native-SoC trip")
        rows = []
        previous = 0.0
        for report in reports:
            if not isinstance(report, dict):
                raise ValueError("Invalid source report")
            t, odo, soc, soc_t = map(
                number,
                (
                    report.get("t"),
                    report.get("odo"),
                    report.get("soc_pct"),
                    report.get("soc_time"),
                ),
            )
            if (
                None in (t, odo, soc, soc_t)
                or t <= previous
                or t > now + 60
                or odo <= 0
                or not 0 <= soc <= 100
                or not -30 <= t - soc_t <= 180
                or not isinstance(report.get("home_connected"), bool)
            ):
                raise ValueError("Invalid chronological native source report")
            rows.append(
                {
                    "t": t,
                    "odo": odo,
                    "soc_pct": soc,
                    "soc_time": soc_t,
                    "odo_time": number(report.get("odo_time", t)),
                    "home_connected_since": number(report.get("home_connected_since")),
                    "home_connected": report["home_connected"],
                }
            )
            previous = t
        digest = sha256(json.dumps(rows, sort_keys=True).encode()).hexdigest()
        if (
            self.data["native_replays"].get(ident, {}).get("digest") == digest
            and not tail
        ):
            return False
        if (
            rows[0]["odo"] != old["start_odo"]
            or rows[-1]["odo"] != (tail or old)["end_odo"]
            or rows[0]["t"] < old["start"] - 180
            or rows[-1]["t"] > max((tail or old)["end"], now)
            or any(
                trip not in (old, tail)
                and trip["start"] < rows[-1]["t"]
                and trip["end"] > rows[0]["t"]
                for trip in self.all_trips()
            )
            or any(
                rows[0]["t"] <= transition["t"] <= rows[-1]["t"]
                for transition in self.data["source_transitions"]
            )
        ):
            raise ValueError("Reports do not cover only the selected trip")
        scratch = Ledger(self.settings)
        original_charges = deepcopy(self.data["charges"])
        scratch.data["charges"] = deepcopy(original_charges)
        for row in rows:
            odo_time = row["odo_time"]
            if odo_time is None or not 0 <= row["t"] - odo_time <= 180:
                raise ValueError("Invalid odometer source clock")
            scratch.observe_native_sources(
                odo_time,
                row["odo"],
                row["soc_time"],
                row["soc_pct"],
                row["home_connected"],
                row["home_connected_since"],
            )
        if not was_active:
            scratch.tick(
                max(now, rows[-1]["t"] + self.settings["trip_idle_minutes"] * 60)
            )
        if (
            len(scratch.all_trips()) != 1
            or (scratch.data["active"] is not None) != was_active
            or scratch.all_trips()[0]["distance_km"]
            != old["distance_km"] + (tail["distance_km"] if tail else 0)
            or scratch.all_trips()[0]["end_odo"] != (tail or old)["end_odo"]
            or scratch.data["charges"] != original_charges
        ):
            raise ValueError("Replay disagrees with archived trip distance or charges")
        replacement = scratch.all_trips()[0]
        replacement["id"] = ident
        replacement["source"] = "native_source_replay"
        if was_active:
            self.data["active"] = replacement
        else:
            self.data["trips"][self.data["trips"].index(old)] = replacement
        if tail:
            self.data["trips"].remove(tail)
        superseded_losses = deepcopy(self.data["parked_losses"])
        self.data["parked_losses"] = [
            loss
            for loss in self.data["parked_losses"]
            if not (rows[0]["t"] <= loss["start"] and loss["end"] <= rows[-1]["t"])
        ] + scratch.data["parked_losses"]
        # A legacy trailing-loss interval can end much later than its only
        # SoC drop. Reallocate only the endpoint delta proved by this replay.
        endpoint_delta = max(0, (tail or old)["end_energy"] - replacement["end_energy"])
        for loss in list(self.data["parked_losses"]):
            if (
                loss["start"] == (tail or old)["last_movement"]
                and loss["end"] > rows[-1]["t"]
                and endpoint_delta > 1e-9
            ):
                amount = min(loss["kwh"], endpoint_delta)
                loss["kwh"] -= amount
                endpoint_delta -= amount
                if loss["kwh"] < 1e-9:
                    self.data["parked_losses"].remove(loss)
        self.data["native_replays"][ident] = {
            "superseded_parked_losses": superseded_losses,
            "superseded_trip": deepcopy(old),
            "superseded_tail": deepcopy(tail),
            "digest": digest,
            "reports": rows,
            "merged_ids": [tail["id"]] if tail else [],
        }
        self.changed()
        return True

    def preferences(self, values):
        allowed = {
            "opening_price_eur_kwh",
            "petrol_l_100km",
            "petrol_eur_l",
            "rated_kwh_100km",
            "currency",
        }
        currency = currency_code(
            values.get("currency", self.data["preferences"]["currency"])
        )
        if currency != self.data["preferences"]["currency"] and any(
            self.data["preferences"].get(key) is not None and key not in values
            for key in ("opening_price_eur_kwh", "petrol_eur_l")
        ):
            raise ValueError(
                "Enter replacement monetary preferences when changing currency"
            )
        updated = {}
        for key, raw in values.items():
            if key not in allowed:
                raise ValueError("Unknown preference")
            if key == "currency":
                updated[key] = currency
                continue
            value = number(raw)
            if raw is not None and (value is None or value < 0):
                raise ValueError("Preference must be finite and nonnegative")
            updated[key] = value
        self.data["preferences"].update(updated)
        self.changed()

    def parked_periods(self, tz=UTC):
        """Expose recorded stationary decreases, joining only touching intervals."""
        periods = []
        for row in sorted(self.data["parked_losses"], key=lambda r: r["start"]):
            if (
                not row.get("complete")
                or number(row.get("kwh")) is None
                or row["kwh"] <= 0
            ):
                continue
            same_month = periods and datetime.fromtimestamp(
                periods[-1]["end"], tz
            ).strftime("%Y-%m") == datetime.fromtimestamp(row["end"], tz).strftime(
                "%Y-%m"
            )
            if same_month and abs(periods[-1]["end"] - row["start"]) < 0.001:
                periods[-1]["end"] = row["end"]
                periods[-1]["kwh"] += row["kwh"]
            else:
                periods.append(
                    {
                        "id": f"parked-{row['start']:.6f}",
                        "start": row["start"],
                        "end": row["end"],
                        "kwh": row["kwh"],
                    }
                )
        for period in periods:
            period["soc_used_pct"] = period["kwh"] / self.settings["capacity_kwh"] * 100
        return list(reversed(periods))

    def snapshot(self, now, tz=UTC):
        local = datetime.fromtimestamp(now, tz)
        midnight = local.replace(hour=0, minute=0, second=0, microsecond=0)
        charges = sorted(
            (
                c
                for c in self.data["charges"].values()
                if c["kind"] != "dismissed" and not c.get("ongoing")
            ),
            key=lambda c: c["end"],
            reverse=True,
        )
        last_charge = max(
            [c["end"] for c in charges if c.get("confirmed")]
            + [
                self.data["last_home_charge"]
                or (self.data["opening"] or {}).get("t", now)
            ]
        )
        periods = {
            "day": midnight.timestamp(),
            "month": midnight.replace(day=1).timestamp(),
            "year": midnight.replace(month=1, day=1).timestamp(),
            "since_charge": last_charge,
        }
        statistics = {
            key: self.statistics(start, now) for key, start in periods.items()
        }
        # Pair the newest 100 km of known native energy and distance. Sparse
        # gaps and charging/source boundaries do not consume the sample budget.
        last = self.data["last"] or {}
        rolling = self.statistics(0, now, 100, native_only=True)
        if last.get("energy_source") != "native_soc":
            rolling = self.statistics(now + 1, now)
        rolling["basis"] = "native_soc_driving"
        rolling["window_km"] = 100
        rolling["calculated_at"] = now
        rolling["remaining_kwh"] = last.get("energy")
        statistics["last_100km"] = rolling
        displayed = self.display_trips(tz)
        active_id = (self.data["active"] or {}).get("id")
        completed = [r for r in displayed if r["id"] != active_id]
        last_trip = max(completed, key=lambda r: r["end"]) if completed else None
        statistics["last_trip"] = (
            self.statistics(last_trip["start"], last_trip["end"], trip=last_trip)
            if last_trip
            else self.statistics(now + 1, now)
        )
        if self.data["active"]:
            active = next(r for r in displayed if r["id"] == active_id)
            statistics["current_trip"] = self.statistics(
                active["start"], active["end"], trip=active
            )
        pref = self.data["preferences"]
        for value in statistics.values():
            consumption = value["consumption_kwh_100km"]
            energy = self.data["last"]["energy"] if self.data["last"] else None
            value["projected_range_km"] = (
                energy / consumption * 100
                if energy is not None and consumption and consumption > 0
                else None
            )
            petrol = number(pref.get("petrol_l_100km"))
            price = number(pref.get("petrol_eur_l"))
            if pref.get("currency", "EUR") != self.currency:
                price = None
            value["petrol_comparison_eur"] = (
                value["distance_km"] / 100 * petrol * price
                if petrol is not None and price is not None
                else None
            )
            value["petrol_saving_eur"] = (
                value["petrol_comparison_eur"] - value["driving_cost_eur"]
                if value["petrol_comparison_eur"] is not None
                and value["driving_cost_eur"] is not None
                and value["cost_complete"]
                else None
            )
        counters = [
            {**c, "statistics": self.statistics(c["start"], now)}
            for c in self.data["counters"]
        ]
        buckets = {}
        for charge in charges:
            date = datetime.fromtimestamp(charge["end"], tz).strftime("%Y-%m-%d")
            bucket = buckets.setdefault(
                date,
                {
                    "date": date,
                    "kwh": 0,
                    "known_cost_eur": 0,
                    "missing": 0,
                    "currency": self.currency,
                    "currency_mismatch_count": 0,
                },
            )
            bucket["kwh"] += charge["kwh"] if charge.get("confirmed") else 0
            matching_currency = charge.get("currency", "EUR") == self.currency
            if charge.get("confirmed") and matching_currency:
                bucket["known_cost_eur"] += charge.get("cost_eur") or 0
            bucket["currency_mismatch_count"] += int(
                charge.get("confirmed") and not matching_currency
            )
            bucket["missing"] += int(
                not charge.get("confirmed")
                or charge.get("cost_eur") is None
                or not matching_currency
            )
        intervals = self.unaccounted_intervals()
        interval_ids = {r["id"] for r in intervals}
        return {
            "currency": self.currency,
            "revision": self.data["revision"],
            "unaccounted_intervals": intervals,
            "stale_gap_resolution_count": sum(
                r["resolution"] == "stale" for r in intervals
            )
            + sum(ident not in interval_ids for ident in self.data["gap_resolutions"]),
            "experience_version": 1,
            "driving_segments": self.cost_segments(),
            "battery_timeline": [
                {
                    "t": r["t"],
                    "soc": r["energy"] / self.settings["capacity_kwh"] * 100,
                    "odo": r["odo"],
                    "connected": r.get("home_connected", False),
                }
                for r in self.data["samples"]
                if r.get("energy_source") == "native_soc"
            ],
            "trip_semantics_version": 2,
            "trips": list(reversed(displayed)),
            "charges": charges,
            "active_home_charge": next(
                (
                    deepcopy(c)
                    for c in self.data["charges"].values()
                    if c.get("ongoing")
                ),
                None,
            ),
            "active_trip_id": (self.data["active"] or {}).get("id"),
            "statistics": statistics,
            "counters": counters,
            "preferences": deepcopy(pref),
            "parked_periods": self.parked_periods(tz),
            "charging_daily": sorted(buckets.values(), key=lambda b: b["date"]),
            "tracking_started": (self.data["opening"] or {}).get("t"),
            "settings": self.settings,
            "last_charge": last_charge,
            "missing_prices": sum(c.get("cost_eur") is None for c in charges),
            "unconfirmed_charges": sum(not c.get("confirmed") for c in charges),
            "cost_basis": (
                "EVCC home energy/export opportunity cost; public receipts; "
                "estimated battery allocation"
            ),
        }
