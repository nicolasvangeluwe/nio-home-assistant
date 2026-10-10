"""Deterministic car ledger. No HA dependency, network calls or destructive edits."""

from copy import deepcopy
from datetime import datetime
from math import isfinite
from uuid import uuid4
from zoneinfo import ZoneInfo


def number(value):
    if isinstance(value, bool) or value is None:
        return None
    try:
        value = float(value)
        return value if isfinite(value) else None
    except (TypeError, ValueError):
        return None


class Ledger:
    def __init__(self, settings=None, data=None):
        from .const import DEFAULTS

        self.settings = {**DEFAULTS, **(settings or {})}
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

    def changed(self):
        self.data["revision"] += 1

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
            # Archived range-based trips are immutable after migration.
            if (
                self.data["source_transition_at"] is not None
                and trip["start"] < self.data["source_transition_at"]
            ):
                continue
            rows = [r for r in samples if trip["start"] <= r["t"] <= trip["end"]]
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
        if incomplete:
            trip["complete"] = False
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
        self, timestamp, odometer, range_km, home_connected=False, *, soc_pct=None
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
        if home_connected:
            self.close_trip()
        if old and old.get("energy_source", "range_estimate") != source:
            # The two energy estimates have different baselines. Never turn
            # their difference into a trip, stationary loss or charge.
            self.close_trip(incomplete=True)
            self.data["source_transition_at"] = t
            self.data["source_transition_energy"] = energy
            self.data["last"] = sample
            self.data["samples"].append(sample)
            self.data["samples"] = self.data["samples"][-2000:]
            self.changed()
            return True
        if not old:
            self.data["opening"] = deepcopy(sample)
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
                complete = delta >= 0 and not charging
                segment = {
                    "start": old["t"],
                    "end": t,
                    "km": distance,
                    "kwh": delta if complete else None,
                    "complete": complete,
                    "sparse": gap,
                    "start_energy": old["energy"],
                    "end_energy": sample["energy"],
                }
                trip["segments"].append(segment)
                trip["distance_km"] += distance
                trip.update(
                    end=t,
                    last_movement=t,
                    end_odo=odo,
                    end_energy=sample["energy"],
                    complete=trip["complete"] and complete,
                )
            elif delta < -self.energy(2):
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
                        "confirmed": False,
                        "energy_basis": source,
                        "cost_basis": "unknown",
                    }
            elif delta > 0 and not home_connected:
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
        # Small samples only; trips and charges are never age-pruned.
        self.data["samples"].append(sample)
        self.data["samples"] = self.data["samples"][-2000:]
        self.changed()
        return True

    def import_home(self, rows):
        changed = False
        for row in rows:
            if not isinstance(row, (list, tuple)) or len(row) < 8:
                continue
            start, end, kwh = map(number, row[1:4])
            if None in (start, end, kwh) or kwh <= 0 or end < start:
                continue
            ident = "home-" + str(row[0])
            existing = self.data["charges"].get(ident, {})
            charge = {
                "id": ident,
                "kind": "home",
                "category": "home",
                "start": start,
                "end": end,
                "kwh": kwh,
                "cost_eur": number(row[5]),
                "reimbursement_eur": number(row[6]),
                "benefit_eur": number(row[7]),
                "solar_pct": number(row[4]),
                "confirmed": True,
                "energy_basis": "charger_meter",
                "cost_basis": "evcc_energy_and_foregone_export",
            }
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
    ):
        charge = self.data["charges"][ident]
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
        if price is not None or receipt is not None:
            charge.update(
                cost_eur=receipt if receipt is not None else price * charge["kwh"],
                price_eur_kwh=price,
                cost_basis="receipt" if receipt is not None else "entered_rate",
                manual_cost=True,
            )
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

    def cost_segments(self):
        """Replay weighted battery stock; unknown opening price never becomes zero."""
        opening = self.data["opening"]
        if not opening:
            return []
        stock = opening["energy"]
        initial_price = number(self.data["preferences"].get("opening_price_eur_kwh"))
        known_energy = stock if initial_price is not None else 0.0
        value = stock * (initial_price or 0)
        events = []
        for charge in self.data["charges"].values():
            if charge["kind"] != "dismissed" and charge["end"] > opening["t"]:
                events.append((charge["end"], 0, "charge", charge))
        for trip in self.all_trips():
            for segment in trip["segments"]:
                events.append((segment["end"], 1, "trip", segment))
        for loss in self.data["parked_losses"]:
            events.append((loss["end"], 1, "parked", loss))
        if self.data["source_transition_at"] is not None:
            events.append(
                (
                    self.data["source_transition_at"],
                    -1,
                    "source_transition",
                    self.data["source_transition_energy"],
                )
            )
        result = []
        for _, _, kind, row in sorted(events, key=lambda x: (x[0], x[1])):
            if kind == "source_transition":
                stock = row
                known_energy = value = 0.0
            elif kind == "charge":
                kwh = row["kwh"]
                # Wall-to-battery losses are unknown; allocation is approximate.
                if stock + kwh > self.settings["capacity_kwh"]:
                    kwh = max(0, self.settings["capacity_kwh"] - stock)
                cost = row.get("cost_eur") if row.get("confirmed") else None
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
                if kind == "trip":
                    result.append(
                        {**row, "cost_eur": energy * price if complete else None}
                    )
                if energy is None:
                    stock = row.get("end_energy", self.settings["capacity_kwh"])
                    known_energy = value = 0.0
                elif stock > 0:
                    fraction = max(0, (stock - energy) / stock)
                    stock *= fraction
                    known_energy *= fraction
                    value *= fraction
        return result

    def statistics(self, start, end, window_km=None, trip=None):
        selected = {(r["start"], r["end"]) for r in trip["segments"]} if trip else None
        segments = [
            r
            for r in self.cost_segments()
            if start <= r["end"] <= end
            and (selected is None or (r["start"], r["end"]) in selected)
        ]
        if window_km is not None:
            result, remaining = [], window_km
            for row in reversed(segments):
                if remaining <= 0:
                    break
                portion = min(remaining, row["km"])
                scale = portion / row["km"]
                result.append(
                    {
                        **row,
                        "km": portion,
                        "kwh": row["kwh"] * scale if row["kwh"] is not None else None,
                        "cost_eur": row["cost_eur"] * scale
                        if row["cost_eur"] is not None
                        else None,
                    }
                )
                remaining -= portion
            segments = list(reversed(result))
        distance = sum(r["km"] for r in segments)
        energy_ok = bool(segments) and all(r["kwh"] is not None for r in segments)
        cost_ok = bool(segments) and all(r["cost_eur"] is not None for r in segments)
        energy = sum(r["kwh"] for r in segments) if energy_ok else None
        cost = sum(r["cost_eur"] for r in segments) if cost_ok else None
        charges = [
            c
            for c in self.data["charges"].values()
            if c["kind"] != "dismissed" and start <= c["end"] <= end
        ]
        confirmed = [c for c in charges if c.get("confirmed")]
        charged = sum(c["kwh"] for c in confirmed)
        known_spend = sum(
            c["cost_eur"] for c in confirmed if c.get("cost_eur") is not None
        )
        complete_spend = all(
            c.get("confirmed") and c.get("cost_eur") is not None for c in charges
        )
        categories = {}
        for category in ("home", "work", "supercharger", "other"):
            rows = [c for c in confirmed if c["category"] == category]
            if rows:
                total = sum(c["kwh"] for c in rows)
                complete = all(c.get("cost_eur") is not None for c in rows)
                spend = sum(c["cost_eur"] for c in rows) if complete else None
                categories[category] = {
                    "kwh": total,
                    "cost_eur": spend,
                    "price_eur_kwh": spend / total
                    if spend is not None and total
                    else None,
                }
        return {
            "distance_km": distance,
            "used_kwh": energy,
            "parked_loss_estimate_kwh": sum(
                r["kwh"]
                for r in self.data["parked_losses"]
                if start <= r["end"] <= end and r["complete"]
            ),
            "soc_used_pct": energy / self.settings["capacity_kwh"] * 100
            if energy is not None
            else None,
            "consumption_kwh_100km": energy / distance * 100
            if energy is not None and distance
            else None,
            "driving_cost_eur": cost,
            "cost_eur_100km": cost / distance * 100
            if cost is not None and distance
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

    def preferences(self, values):
        allowed = {
            "opening_price_eur_kwh",
            "petrol_l_100km",
            "petrol_eur_l",
            "rated_kwh_100km",
        }
        for key, raw in values.items():
            if key not in allowed:
                raise ValueError("Unknown preference")
            value = number(raw)
            if raw is not None and (value is None or value < 0):
                raise ValueError("Preference must be finite and nonnegative")
            self.data["preferences"][key] = value
        self.changed()

    def parked_periods(self, timezone="UTC"):
        """Expose recorded stationary decreases, joining only touching intervals."""
        periods = []
        tz = ZoneInfo(timezone)
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

    def snapshot(self, now, timezone="UTC"):
        tz = ZoneInfo(timezone)
        local = datetime.fromtimestamp(now, tz)
        midnight = local.replace(hour=0, minute=0, second=0, microsecond=0)
        charges = sorted(
            (c for c in self.data["charges"].values() if c["kind"] != "dismissed"),
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
        statistics["last_100km"] = self.statistics(last_charge, now, 100)
        completed = self.data["trips"]
        last_trip = max(completed, key=lambda r: r["end"]) if completed else None
        statistics["last_trip"] = (
            self.statistics(last_trip["start"], last_trip["end"], trip=last_trip)
            if last_trip
            else self.statistics(now + 1, now)
        )
        if self.data["active"]:
            active = self.data["active"]
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
            value["petrol_comparison_eur"] = (
                value["distance_km"] / 100 * petrol * price
                if petrol is not None and price is not None
                else None
            )
            value["petrol_saving_eur"] = (
                value["petrol_comparison_eur"] - value["driving_cost_eur"]
                if value["petrol_comparison_eur"] is not None
                and value["driving_cost_eur"] is not None
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
                date, {"date": date, "kwh": 0, "known_cost_eur": 0, "missing": 0}
            )
            bucket["kwh"] += charge["kwh"] if charge.get("confirmed") else 0
            bucket["known_cost_eur"] += charge.get("cost_eur") or 0
            bucket["missing"] += int(
                not charge.get("confirmed") or charge.get("cost_eur") is None
            )
        return {
            "revision": self.data["revision"],
            "trips": list(reversed(self.all_trips())),
            "charges": charges,
            "active_trip_id": (self.data["active"] or {}).get("id"),
            "statistics": statistics,
            "counters": counters,
            "preferences": deepcopy(pref),
            "parked_periods": self.parked_periods(timezone),
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
